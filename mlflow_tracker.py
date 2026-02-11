"""
MLflow Tracking Utilities
Handles experiment tracking and logging
"""
import mlflow
import os
from typing import Dict, Any, Optional
from datetime import datetime
from config import Config


class MLflowTracker:
    """Track experiments and runs with MLflow"""
    
    def __init__(self, experiment_name: str = Config.EXPERIMENT_NAME):
        # Set tracking URI
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set or create experiment
        self.experiment_name = experiment_name
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment is None:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        else:
            self.experiment_id = experiment.experiment_id
        
        mlflow.set_experiment(experiment_name)
        
        self.current_run_id = None
    
    def start_run(self, run_name: Optional[str] = None) -> str:
        """Start a new MLflow run"""
        if run_name is None:
            run_name = f"study_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        run = mlflow.start_run(run_name=run_name)
        self.current_run_id = run.info.run_id
        
        return self.current_run_id
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters"""
        for key, value in params.items():
            try:
                mlflow.log_param(key, value)
            except Exception as e:
                print(f"Failed to log param {key}: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics"""
        for key, value in metrics.items():
            try:
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value, step=step)
            except Exception as e:
                print(f"Failed to log metric {key}: {e}")
    
    def log_artifact(self, file_path: str):
        """Log an artifact file"""
        try:
            mlflow.log_artifact(file_path)
        except Exception as e:
            print(f"Failed to log artifact {file_path}: {e}")
    
    def log_text(self, text: str, artifact_file: str):
        """Log text content as an artifact"""
        try:
            mlflow.log_text(text, artifact_file)
        except Exception as e:
            print(f"Failed to log text artifact {artifact_file}: {e}")
    
    def log_dict(self, dictionary: Dict, artifact_file: str):
        """Log dictionary as JSON artifact"""
        try:
            mlflow.log_dict(dictionary, artifact_file)
        except Exception as e:
            print(f"Failed to log dict artifact {artifact_file}: {e}")
    
    def set_tags(self, tags: Dict[str, str]):
        """Set tags for the current run"""
        for key, value in tags.items():
            try:
                mlflow.set_tag(key, value)
            except Exception as e:
                print(f"Failed to set tag {key}: {e}")
    
    def end_run(self, status: str = "FINISHED"):
        """End the current run"""
        try:
            mlflow.end_run(status=status)
            self.current_run_id = None
        except Exception as e:
            print(f"Failed to end run: {e}")
    
    def log_study_session(
        self,
        input_type: str,
        num_questions: int,
        difficulty: str,
        processing_time: float,
        summary_length: int,
        num_key_points: int,
        success: bool = True
    ):
        """Log a complete study session"""
        
        # Log parameters
        self.log_params({
            "input_type": input_type,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "model_name": Config.MODEL_NAME,
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP
        })
        
        # Log metrics
        self.log_metrics({
            "processing_time_seconds": processing_time,
            "summary_length": summary_length,
            "num_key_points": num_key_points,
            "num_questions_generated": num_questions,
            "success": 1.0 if success else 0.0
        })
        
        # Log tags
        self.set_tags({
            "status": "success" if success else "failed",
            "input_type": input_type,
            "difficulty": difficulty
        })
    
    def get_run_info(self) -> Optional[Dict]:
        """Get information about the current run"""
        if self.current_run_id:
            run = mlflow.get_run(self.current_run_id)
            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "artifact_uri": run.info.artifact_uri
            }
        return None


def get_mlflow_ui_url(tracking_uri: str = "./mlruns") -> str:
    """Get the URL to launch MLflow UI"""
    return f"mlflow ui --backend-store-uri {tracking_uri}"