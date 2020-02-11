class Settings:

    def __init__(self):
        self.width = 30  # Cell
        self.height = 20    # Cell
        self.obstaclePercent = 10   # Percent

        self.mutation = 50  # Percent
        self.elitism = 3  # Percent
        self.mutationProp = .7

        self.populationSize = max(150, int(self.width * self.height / 3))

        self.drawType = 1  # Values = 0 and higher integers




