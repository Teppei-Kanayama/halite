from kaggle_environments import make
env = make("halite", debug=True)
env.run(["main.py", "random", "random", "random"])
