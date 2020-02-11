from World import *

def main():
    while True:
        try:
            world = World()
            if not world.generatePopulation():
                world.win.close()
                continue
            world.evolve()
            world.plot()
        except:
            exit(0)

if __name__ == "__main__":
    main()
