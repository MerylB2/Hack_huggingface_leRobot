import modal
import subprocess
import os

# Define the image with all necessary dependencies

# Complete LeRobot image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install([
        "git", "curl", "cmake", "build-essential", "python3-dev", 
        "pkg-config", "libavformat-dev", "libavcodec-dev", 
        "libavdevice-dev", "libavutil-dev", "libswscale-dev", 
        "libswresample-dev", "libavfilter-dev", "ffmpeg"
    ])
    .pip_install([
        "torch==2.2.2",
        "torchvision>=0.15.0",
        "torchaudio",
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "pillow>=9.0.0",
        "gymnasium>=0.28.0",
        "wandb",
        "tensorboard",
        "matplotlib",
        "seaborn",
        "pandas",
        "scipy",
        "scikit-learn",
        "h5py",
        "pyyaml",
        "omegaconf",
        "hydra-core",
        "ffmpeg-python",
        "gym-pusht",
        "lerobot[smolvla]",
        "transformers",
        "accelerate",
        "num2words",
        "datasets",
        "torch-optimizer",
        "draccus"
    ])
    .run_commands([
        "git clone https://github.com/huggingface/lerobot.git /lerobot",
        "cd /lerobot && pip install -e ."
    ])
    .workdir("/lerobot")
)


app = modal.App("lerobot-smolvla", image=image)


# Create a volume for persistent data storage
volume = modal.Volume.from_name("lerobot-outputs", create_if_missing=True)

@app.function(
    gpu="L40S",
    timeout=3600, 
    volumes={"/outputs": volume},
    secrets=[modal.Secret.from_name("wandb-secret")],  # Optional: for W&B logging
    container_idle_timeout=600
)
def train_policy(
    dataset_repo_id: str = "lerobot/pusht",
    policy_path: str = "act",
    output_dir: str = "/outputs/train_run"
):
    import os
    os.environ["PYTHONUNBUFFERED"] = "1"
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token:
        raise EnvironmentError("HUGGINGFACE_TOKEN environment variable is not set. Please set it before running the training.")
    os.environ["HF_TOKEN"] = hf_token
    
    cmd = [
        "python", "lerobot/scripts/train.py",
        f"--dataset.repo_id={dataset_repo_id}",
        f"--policy.path={policy_path}",
        f"--batch_size=64",
        f"--steps=20000",
        f"--output_dir={output_dir}",
        "--policy.device=cuda",
        "--wandb.enable=true"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/lerobot")
   
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    # Commit volume changes
    volume.commit()
    
    return {
        "return_code": result.returncode,
        "output_dir": output_dir,
        "success": result.returncode == 0
    }

@app.local_entrypoint()
def main():
    # Launch training
    result = train_policy.remote(
        dataset_repo_id="lerobot/svla_so101_pickplace",
        policy_path="lerobot/smolvla_base",
        output_dir = "/outputs/train_smolvla"
    )
    print(f"Training completed with result: {result}")
