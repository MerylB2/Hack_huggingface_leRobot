# Modal Inference with LeRobot

This project demonstrates how to run training for LeRobot on a cloud GPU using Modal. The test script is designed to be executed through Poetry for dependency management.

## Prerequisites

1. **Python**: Ensure you have Python 3.12.9 installed.
2. **Poetry**: Install Poetry for dependency management. You can install it using:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. **Modal**: Set up Modal CLI and authenticate. Follow the instructions at [Modal Documentation](https://modal.com/docs/guide/cli).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/huggingface/lerobot.git
   cd lerobot
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Ensure you have the required secrets and volumes set up in Modal:
   - Create a secret named `wandb-secret` for Weights & Biases logging.
   - Create a volume named `lerobot-outputs` for persistent data storage.

## Running the Test Script

1. Activate the Poetry shell:
   ```bash
   poetry shell
   ```

2. Run the test script using Modal:
   ```bash
   modal run lerobot-test.py
   ```

## Script Overview

The test script (`lerobot-test.py`) performs the following:
- Sets up a Modal image with all necessary dependencies for LeRobot.
- Defines a training function (`train_policy`) that runs the training script on a cloud GPU.
- Uses Modal's persistent volume to store training outputs.
- Logs training progress to Weights & Biases (optional).

## Customizing Training Parameters

You can customize the training parameters by modifying the `train_policy` function in `lerobot-test.py`. For example:
- `dataset_repo_id`: Specify the dataset repository ID.
- `policy_type`: Choose the policy type (e.g., "act", "diffusion").
- `env_type`: Define the environment type (e.g., "pusht").
- `output_dir`: Set the output directory for training results.

## Example Output

After running the script, you should see logs indicating the progress of the training. The results will be stored in the specified output directory (`/outputs/train_run` by default).

## Troubleshooting

- Ensure all dependencies are installed correctly using Poetry.
- Verify that Modal CLI is authenticated and configured properly.
- Check that the required secrets and volumes are set up in Modal.

For further assistance, refer to the [Modal Documentation](https://modal.com/docs) or the [LeRobot Repository](https://github.com/huggingface/lerobot).
