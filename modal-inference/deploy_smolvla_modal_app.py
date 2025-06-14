import modal
import subprocess
import os

# Define the image with all necessary dependencies for SmolVLA
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
        "lerobot[smolvla]",  # Specific dependency for SmolVLA
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

# Define the Modal App
app = modal.App("lerobot-smolvla-training-app", image=image)

# Create a volume for persistent data storage
volume = modal.Volume.from_name("lerobot-smolvla-training-volume", create_if_missing=True)

@app.function(
    gpu="L40S",  # Specify GPU type
    timeout=7200,  # Increased timeout to 2 hours for longer training runs
    volumes={"/outputs": volume},  # Mount the volume for outputs
    secrets=[modal.Secret.from_name("wandb-secret")],  # Optional: for W&B logging
    container_idle_timeout=600  # Idle timeout for the container
)
def train_policy(
    dataset_repo_id: str = "lerobot/svla_so101_pickplace",  # Default dataset for SmolVLA
    policy_path: str = "lerobot/smolvla_base",  # Default policy config for SmolVLA
    output_dir: str = "/outputs/train_smolvla_run", # Default output directory
    batch_size: int = 64,
    steps: int = 20000
):
    import os
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    # Ensure Hugging Face token is available
    hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token:
        raise EnvironmentError("HUGGINGFACE_TOKEN environment variable is not set. Please set it in your Modal environment secrets.")
    os.environ["HF_TOKEN"] = hf_token
    
    cmd = [
        "python", "lerobot/scripts/train.py",
        f"--dataset.repo_id={dataset_repo_id}",
        f"--policy.path={policy_path}",
        f"--batch_size={batch_size}",
        f"--steps={steps}",
        f"--output_dir={output_dir}",
        "--policy.device=cuda",  # Ensure training on GPU
        "--wandb.enable=true"    # Enable W&B logging (requires wandb-secret)
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute the training script
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/lerobot")
   
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    # Commit volume changes to persist the output
    volume.commit()
    
    return {
        "return_code": result.returncode,
        "output_dir": output_dir,
        "success": result.returncode == 0,
        "stdout_tail": result.stdout[-1000:], # Last 1000 chars of stdout
        "stderr_tail": result.stderr[-1000:], # Last 1000 chars of stderr
    }

# @app.local_entrypoint()
# def main():
#     # Example: Launch training for SmolVLA on a specific dataset
#     print("Starting SmolVLA training...")
#     result = train_policy.remote(
#         dataset_repo_id="lerobot/svla_so101_pickplace", # Example dataset
#         policy_path="lerobot/smolvla_base",             # SmolVLA base configuration
#         output_dir="/outputs/train_smolvla_svla_so101", # Specific output directory in the volume
#         steps=20000 # Number of training steps
#     )
#     print(f"Training completed.")
#     print(f"Success: {result['success']}")
#     print(f"Output directory: {result['output_dir']}")
#     print(f"Return code: {result['return_code']}")
#     if not result['success']:
#         print("Error during training. Check logs.")
#         print("STDOUT (tail):", result['stdout_tail'])
#         print("STDERR (tail):", result['stderr_tail'])

# To deploy this app:
# 1. Ensure you have Modal CLI installed and configured.
# 2. Ensure HUGGINGFACE_TOKEN is set as a Modal secret (e.g., modal secret create huggingface HUGGINGFACE_TOKEN=your_hf_token).
# 3. Ensure WANDB_API_KEY is set as a Modal secret named "wandb-secret" (e.g., modal secret create wandb-secret WANDB_API_KEY=your_wandb_key).
# 4. Run `modal deploy deploy_smolvla_modal_app.py`.
# To run the training after deployment (or locally for testing):
# `modal run deploy_smolvla_modal_app.py`
