# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: tests

PYTHON_PATH := $(shell which python)

# If uv is installed and a virtual environment exists, use it
UV_CHECK := $(shell command -v uv)
ifneq ($(UV_CHECK),)
	PYTHON_PATH := $(shell .venv/bin/python)
endif

export PATH := $(dir $(PYTHON_PATH)):$(PATH)

DEVICE ?= cpu

HF_USER="Razane-1"
DATASET_NAME="${HF_USER}/record-test"
SINGLE_TASK="grab a card and put it on the table"
EVAL_RUNS = 1 2 3 4 5

build-cpu:
	docker build -t lerobot:latest -f docker/lerobot-cpu/Dockerfile .

build-gpu:
	docker build -t lerobot:latest -f docker/lerobot-gpu/Dockerfile .

test-end-to-end:
	${MAKE} DEVICE=$(DEVICE) test-act-ete-train
	${MAKE} DEVICE=$(DEVICE) test-act-ete-train-resume
	${MAKE} DEVICE=$(DEVICE) test-act-ete-eval
	${MAKE} DEVICE=$(DEVICE) test-diffusion-ete-train
	${MAKE} DEVICE=$(DEVICE) test-diffusion-ete-eval
	${MAKE} DEVICE=$(DEVICE) test-tdmpc-ete-train
	${MAKE} DEVICE=$(DEVICE) test-tdmpc-ete-eval

test-act-ete-train:
	python lerobot/scripts/train.py \
		--policy.type=act \
		--policy.dim_model=64 \
		--policy.n_action_steps=20 \
		--policy.chunk_size=20 \
		--policy.device=$(DEVICE) \
		--env.type=aloha \
		--env.episode_length=5 \
		--dataset.repo_id=lerobot/aloha_sim_transfer_cube_human \
		--dataset.image_transforms.enable=true \
		--dataset.episodes="[0]" \
		--batch_size=2 \
		--steps=4 \
		--eval_freq=2 \
		--eval.n_episodes=1 \
		--eval.batch_size=1 \
		--save_freq=2 \
		--save_checkpoint=true \
		--log_freq=1 \
		--wandb.enable=false \
		--output_dir=tests/outputs/act/

test-act-ete-train-resume:
	python lerobot/scripts/train.py \
		--config_path=tests/outputs/act/checkpoints/000002/pretrained_model/train_config.json \
		--resume=true

test-act-ete-eval:
	python lerobot/scripts/eval.py \
		--policy.path=tests/outputs/act/checkpoints/000004/pretrained_model \
		--policy.device=$(DEVICE) \
		--env.type=aloha \
		--env.episode_length=5 \
		--eval.n_episodes=1 \
		--eval.batch_size=1

test-diffusion-ete-train:
	python lerobot/scripts/train.py \
		--policy.type=diffusion \
		--policy.down_dims='[64,128,256]' \
		--policy.diffusion_step_embed_dim=32 \
		--policy.num_inference_steps=10 \
		--policy.device=$(DEVICE) \
		--env.type=pusht \
		--env.episode_length=5 \
		--dataset.repo_id=lerobot/pusht \
		--dataset.image_transforms.enable=true \
		--dataset.episodes="[0]" \
		--batch_size=2 \
		--steps=2 \
		--eval_freq=2 \
		--eval.n_episodes=1 \
		--eval.batch_size=1 \
		--save_checkpoint=true \
		--save_freq=2 \
		--log_freq=1 \
		--wandb.enable=false \
		--output_dir=tests/outputs/diffusion/

test-diffusion-ete-eval:
	python lerobot/scripts/eval.py \
		--policy.path=tests/outputs/diffusion/checkpoints/000002/pretrained_model \
		--policy.device=$(DEVICE) \
		--env.type=pusht \
		--env.episode_length=5 \
		--eval.n_episodes=1 \
		--eval.batch_size=1

test-tdmpc-ete-train:
	python lerobot/scripts/train.py \
		--policy.type=tdmpc \
		--policy.device=$(DEVICE) \
		--env.type=xarm \
		--env.task=XarmLift-v0 \
		--env.episode_length=5 \
		--dataset.repo_id=lerobot/xarm_lift_medium \
		--dataset.image_transforms.enable=true \
		--dataset.episodes="[0]" \
		--batch_size=2 \
		--steps=2 \
		--eval_freq=2 \
		--eval.n_episodes=1 \
		--eval.batch_size=1 \
		--save_checkpoint=true \
		--save_freq=2 \
		--log_freq=1 \
		--wandb.enable=false \
		--output_dir=tests/outputs/tdmpc/

test-tdmpc-ete-eval:
	python lerobot/scripts/eval.py \
		--policy.path=tests/outputs/tdmpc/checkpoints/000002/pretrained_model \
		--policy.device=$(DEVICE) \
		--env.type=xarm \
		--env.episode_length=5 \
		--env.task=XarmLift-v0 \
		--eval.n_episodes=1 \
		--eval.batch_size=1

cal-lead:
	python -m lerobot.calibrate \
        --teleop.type=so100_leader \
        --teleop.port=/dev/tty.usbmodem58760432281 \
        --teleop.id=leader

cal-fol:
	python -m lerobot.calibrate \
        --robot.type=so100_follower \
        --robot.port=/dev/tty.usbmodem58760434471 \
        --robot.id=follower

tele:
	python -m lerobot.teleoperate \
        --robot.type=so100_follower \
        --robot.port=/dev/tty.usbmodem58760434471 \
        --robot.id=follower \
        --teleop.type=so100_leader \
        --teleop.port=/dev/tty.usbmodem58760432281 \
        --teleop.id=leader \

telecam:
	python -m lerobot.teleoperate \
        --robot.type=so100_follower \
        --robot.port=/dev/tty.usbmodem58760434471 \
        --robot.id=follower \
		--robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
        --teleop.type=so100_leader \
        --teleop.port=/dev/tty.usbmodem58760432281 \
        --teleop.id=leader \
        --display_data=true

record:
	python -m lerobot.record \
		--robot.type=so100_follower \
		--robot.port=/dev/tty.usbmodem58760434471 \
		--robot.id=follower \
		--robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
		--teleop.type=so100_leader \
		--teleop.port=/dev/tty.usbmodem58760432281 \
		--teleop.id=leader \
		--display_data=true \
		--dataset.repo_id=${HF_USER}/${DATASET_NAME} \
		--dataset.num_episodes=70 \
		--dataset.single_task=${SINGLE_TASK} \
		--dataset.episode_time_s=30 \
		--dataset.reset_time_s=10

eval:
	python -m lerobot.record \
      --robot.type=so100_follower \
      --robot.port=/dev/tty.usbmodem58760434471 \
      --robot.id==follower \
      --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
      --dataset.single_task="Throw the dice" \
      --dataset.repo_id="Razane-1/eval_record-test" \
      --policy.path="Razane-1/model_checkpoints" \
      --dataset.episode_time_s=120 \
      --dataset.num_episodes=50

eval-multiple-runs:
	@for run in $(EVAL_RUNS); do \
		echo "=== Evaluation run $$run/5 ==="; \
		python -m lerobot.record \
			--robot.type=so100_follower \
			--robot.port=/dev/tty.usbmodem58760434471 \
			--robot.id=follower \
			--robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
			--dataset.single_task="Throw the dice" \
			--dataset.repo_id="Razane-1/eval_record-test_run$$run" \
			--policy.path="Razane-1/model_checkpoints" \
			--dataset.episode_time_s=120 \
			--dataset.num_episodes=50; \
		sleep 5; \
		rm -rf /Users/marieangeferracci/.cache/huggingface/lerobot/Razane-1/eval_record-test; \
	done
