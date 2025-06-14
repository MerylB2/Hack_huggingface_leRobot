import modal
import subprocess

# Define the image with all necessary dependencies
import modal

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
        "torch>=2.0.0,<2.4.0",
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
        "lerobot[pusht]"  
    ])
    .run_commands([
        "git clone https://github.com/huggingface/lerobot.git /lerobot",
        "cd /lerobot && pip install -e ."
    ])
    .workdir("/lerobot")
)


app = modal.App("lerobot-training", image=image)

# Create a volume for persistent data storage
volume = modal.Volume.from_name("lerobot-outputs", create_if_missing=True)

@app.function(
    gpu="A100",
    timeout=7200,  # 2 hours
    volumes={"/outputs": volume},
    secrets=[modal.Secret.from_name("wandb-secret")]  # Optional: for W&B logging
)
def train_policy(
    dataset_repo_id: str = "lerobot/pusht",
    policy_type: str = "act",
    env_type: str = "pusht",
    output_dir: str = "/outputs/train_run"
):
    import os
    os.environ["PYTHONUNBUFFERED"] = "1"
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
    
    cmd = [
        "python", "lerobot/scripts/train.py",
        f"--dataset.repo_id={dataset_repo_id}",
        f"--policy.type={policy_type}",
        f"--env.type={env_type}",
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
        dataset_repo_id="lerobot/pusht",
        policy_type="diffusion",
        env_type="pusht"
    )
    print(f"Training completed with result: {result}")
