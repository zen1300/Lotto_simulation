from simulator import Lotto


if __name__ == '__main__':
    sim = Lotto()
    sim.run(jackpot=250_000_000, add_powerplay=True, num_plays=100_000)
    print(sum(sim.winnings))
    sim.view_results()