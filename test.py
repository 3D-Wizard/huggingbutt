from huggingbutt.env import Env
from huggingbutt.agent import Agent
from stable_baselines3.ppo import PPO
from stable_baselines3.common.policies import ActorCriticPolicy



if __name__ == '__main__':
    env = Env.get("HuggingButt/juggle", 'mac', startup_args=['--time_scale', '10'])
    agent = Agent(
        algorithm=PPO,
        policy=ActorCriticPolicy,
        env=env
    )
    agent.learn(total_timesteps=8000)
    agent.save()
    env.close()





