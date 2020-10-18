import random
import pandas as pd
import plotly


class Lotto:
    """
    Class used for simulating powerball lotto drawings. Exposes various methods for running and viewing simulation
    results.

    Use the .run() method to run a simulation with the desired arguments.

    Ex:
        sim = Lotto()

        sim.run()

    After running, the Lotto object will keep a running total of various properties of each simulation. These results
    can be exported to a .csv file or viewed in a subplot:

    Ex:
        sim.export_results()

        sim.view_results()
    """
    def __init__(self):
        self._balls = tuple(i for i in range(1, 70))
        self._powerball = tuple(i for i in range(1, 27))
        self._powerplays = (2, 3, 4, 5, 10)
        # dict of {matches: prize money}
        self._prizes = {
            '0 + powerball': 4,
            '1 + powerball': 4,
            '2 + powerball': 7,
            '3 + no powerball': 7,
            '3 + powerball': 100,
            '4 + no powerball': 100,
            '4 + powerball': 50_000,
            '5 + no powerball': 1_000_000,
            '5 + powerball': 'jackpot'
        }
        # Keep internal results of every consecutive play
        self.plays = 0
        self.spent = []
        self.winnings = []
        self.chosen_ball1 = []
        self.chosen_ball2 = []
        self.chosen_ball3 = []
        self.chosen_ball4 = []
        self.chosen_ball5 = []
        self.chosen_powerball = []
        self.chosen_powerplay = []

    @staticmethod
    def _multiply_powerplay(winnings, powerplay):
        """
        Return the updated winnings after applying the powerplay. Per powerball rules, if base prize was 1,000,000,
        then the maximum powerplay prize is 2,000,000 regardless of actual multiplier. If no powerplay was added
        (powerplay = 0), then will return base winnings.
        :param winnings: Value of base powerball winnings.
        :type winnings: int
        :param powerplay: Chosen powerplay multiplier.
        :type powerplay: int
        :return: Winnings * powerplay except for 1,000,000 prize which instead returns 2,000,000.
        :rtype: int
        """
        if powerplay > 0:
            if winnings < 1_000_000:
                return winnings * powerplay
            else:
                return 2_000_000
        return winnings

    def _draw(self, jackpot):
        """
        Simulates a random draw of 5 normal lotto balls, 1 powerball, and 1 powerplay multiplier. Note: powerplay
        multiplier of x10 is only available for jackpots <= 150,000,000.
        :param jackpot: Amount of current jackpot. Used to set powerplay multiplier options.
        :type jackpot: int
        :return: Individual lists of chosen lotto balls, powerplay ball, and powerplay multiplier.
        :rtype: tuple[list[int], list[int], list[int]]
        """
        balls = random.sample(self._balls, 5)
        powerball = random.sample(self._powerball, 1)
        if jackpot >= 150_000_000:
            powerplay = random.sample(self._powerplays, 1)
        else:
            # x10 powerplay is only for jackpots > 150,000,000
            _powerplays = (2, 3, 4, 5)
            powerplay = random.sample(_powerplays, 1)

        return balls, powerball, powerplay

    def run(self, jackpot=150_000_000, add_powerplay=False, num_plays=5000):
        """
        Run a simulated powerball drawing. Simulates a unique drawing for every play in num_plays.
        For every play, will update the following properties with the results:

            Lotto.plays = Number total plays.

            Lotto.spent = List of cost of each play.

            Lotto.winnings = List of winnings of each play.

            Lotto.chosen_ball(1-5) = List of the selected number for the ball position (1-5) of each play.

            Lotto.chosen_powerball = List of the selected powerball of each play.

            Lotto.chosen_powerplay = List of the selected powerplay of each play.
        :param jackpot: Value of jackpot.
        :type jackpot: int
        :param add_powerplay: Whether to add a powerplay option or not.
        :type add_powerplay: bool
        :param num_plays: Number of drawings to simulate.
        :type num_plays: int
        """
        for play in range(num_plays):
            # update internal properties
            self.plays += 1
            spent = 2 if not add_powerplay else 3
            self.spent.append(spent)

            # perform random drawing for the user ticket and the lotto drawing
            ticket_balls, ticket_powerball, _ = self._draw(jackpot)
            chosen_balls, chosen_powerball, powerplay = self._draw(jackpot)
            self.chosen_ball1.append(ticket_balls[0])
            self.chosen_ball2.append(ticket_balls[1])
            self.chosen_ball3.append(ticket_balls[2])
            self.chosen_ball4.append(ticket_balls[3])
            self.chosen_ball5.append(ticket_balls[4])
            self.chosen_powerball.append(ticket_powerball[0])
            self.chosen_powerplay.append(powerplay[0])

            # compare results of lotto to user ticket
            matched_balls = len([i for i in ticket_balls if i in chosen_balls])
            matched_powerball = 'powerball' if ticket_powerball == chosen_powerball else 'no powerball'

            # update winnings based on results, jackpot, and powerplay
            try:
                winnings = self._prizes[f'{matched_balls} + {matched_powerball}']
            except KeyError:
                winnings = 0
            if winnings == 'jackpot':
                winnings = jackpot
            else:
                if add_powerplay:
                    winnings = self._multiply_powerplay(winnings, powerplay[0])
            self.winnings.append(winnings)

    def export_results(self, file_path):
        """
        Report the results for each individual play to a .csv file.
        :param file_path: File path of output file.
        :type file_path: str
        """
        data = {
            'Ticket Number': [i for i in range(1, self.plays + 1)],
            'Money Spent': self.spent,
            'Money Won': self.winnings,
            'Ball 1': self.chosen_ball1,
            'Ball 2': self.chosen_ball2,
            'Ball 3': self.chosen_ball3,
            'Ball 4': self.chosen_ball4,
            'Ball 5': self.chosen_ball5,
            'Powerball': self.chosen_powerball,
            'Powerplay': self.chosen_powerplay
        }
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

    def view_results(self):
        pass
