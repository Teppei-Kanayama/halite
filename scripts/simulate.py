from kaggle_environments import make
env = make("halite", debug=True, configuration={"size": 21})
env.run(["halite/agent.py", "agents/submission_0628T1404.py", "agents/submission_0628T1404.py", "agents/halite_swarm_intelligence.py"])
