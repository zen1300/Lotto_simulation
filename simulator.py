import random

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import interp1d


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
        self.net_profit = 0
        self.chosen_ball1 = []
        self.chosen_ball2 = []
        self.chosen_ball3 = []
        self.chosen_ball4 = []
        self.chosen_ball5 = []
        self.chosen_powerball = []
        self.chosen_powerplay = []

    @staticmethod
    def _create_histogram(x, **kwargs):
        """
        Create and return a histogram graph object that can be added to a plotly Figure or subplot.
        :param x: Array of data to calculate histogram.
        :type x: list
        :param kwargs: Any plotly go.Histogram() kwargs
        :type kwargs:
        :return: A plotly go.Histogram()
        :rtype: object
        """
        fig = go.Histogram(
            x=x,
            **kwargs
        )
        return fig

    @staticmethod
    def _create_scatter(x, y, **kwargs):
        """
        Create and return a scatter graph object that can be added to a plotly Figure or subplot.
        :param x: Array of x data.
        :type x: list
        :param y: Array of y data
        :type y: list
        :param kwargs: Any plotly go.Scatter() kwargs
        :type kwargs:
        :return: A plotly go.Scatter()
        :rtype: object
        """
        fig = go.Scatter(
            x=x,
            y=y,
            mode='lines',
            **kwargs
        )
        return fig

    @staticmethod
    def _create_waterfall(x, y, **kwargs):
        """
        Create and return a waterfall graph object that can be added to a plotly Figure or subplot.
        :param x: Array of x data
        :type x: list
        :param y: Array of relative change of y data
        :type y: list
        :param kwargs: Any plotly go.Waterfall() kwargs
        :type kwargs:
        :return: A plotly go.Waterfall()
        :rtype: object
        """
        fig = go.Waterfall(
            x=x,
            y=y,
            **kwargs
        )
        return fig

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

    @staticmethod
    def _smooth_fit(x_values, y_values, interpolation='linear', points=5_000):
        """
        Perform and return interpolation of x_values and y_values. Useful for graphing to help increase performance by
        limiting number of points.
        :param x_values: Original list of x values.
        :type x_values: list or numpy.ndarray
        :param y_values: Original list of y values.
        :type y_values: list or numpy.ndarray
        :param interpolation: Type of interpolation to perform. Options from scipy.interpolation.interp1d:
            ‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’, ‘next’.
            Defaults to linear.
        :type interpolation: str
        :param points: Number of points to return for interpolated values. Defaults to 5,000
        :type points: int
        :return: Interpolated x and y of ('x_values', 'y_values') by 'interpolation' with size 'points'.
        :rtype: (numpy.ndarray, numpy.ndarray)
        """
        interp = interp1d(x_values, y_values, kind=interpolation)
        x_points = np.linspace(min(x_values), max(x_values), points)
        y_fit = interp(x_points)
        return x_points, y_fit

    def _calc_profit(self):
        """
        Calculate and return the running cumulative sum of profits for each play.
        :return: The cumulative sum of profits for each play
        :rtype: numpy.ndarray
        """
        spent = np.negative(self.spent)
        won = np.asarray(self.winnings)
        profit = spent + won
        return profit

    def _draw(self, jackpot):
        """
        Simulates a random draw of 5 normal lotto balls, 1 powerball, and 1 powerplay multiplier. Note: powerplay
        multiplier of x10 is only available for jackpots < 150,000,000.
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
            # x10 powerplay is only for jackpots < 150,000,000
            _powerplays = (2, 3, 4, 5)
            powerplay = random.sample(_powerplays, 1)

        return balls, powerball, powerplay

    def _get_all_balls(self):
        """
        Return a merged list of all individual lotto balls drawn.
        :return: List of all lotto balls drawn.
        :rtype: list
        """
        return self.chosen_ball1 + self.chosen_ball2 + self.chosen_ball3 + self.chosen_ball4 + self.chosen_ball5

    def _get_df(self):
        """
        Convert and return lotto results in form of pandas DataFrame.

        Columns:
            Ticket Number, Money Spent, Money Won, Ball 1, Ball 2, Ball 3, Ball 4, Ball 5, Powerball, Powerplay
        :return: Pandas DataFrame containing results for each play.
        :rtype: pandas.DataFrame
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
        return df

    def run(self, jackpot=150_000_000, add_powerplay=False, num_plays=5000):
        """
        Run a simulated powerball drawing. Simulates a unique drawing for every play in num_plays.
        For every play, will update the following properties with the results:
            - Lotto.plays = Number total plays.
            - Lotto.spent = List of cost of each play.
            - Lotto.winnings = List of winnings of each play.
            - Lotto.chosen_ball(1-5) = List of the selected number for the ball position (1-5) of each play.
            - Lotto.chosen_powerball = List of the selected powerball of each play.
            - Lotto.chosen_powerplay = List of the selected powerplay of each play.
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
        self.net_profit = np.sum(self._calc_profit())

    def export_results(self, file_path):
        """
        Report the results for each individual play to a .csv file.
        :param file_path: File path of output file.
        :type file_path: str
        """
        df = self._get_df()
        df.to_csv(file_path, index=False)

    def view_results(self, max_points=5_000):
        """
        View the results of all lotto plays.

        Creates graphs for:
            - Distribution of lottery balls selected.
            - Distribution of powerballs selected.
            - Scatters of money spent and won.
            - Waterfall graph of cumulative profit per play.
        :param max_points: Maximum number of points to graph. A large number of points will cause slow performance.
            If # of plays > max_points, will interpolate results down to max_points. As such, the general trends of the
            graphs may be accurate, but the exact play-specific data may not.
        :type max_points: int
        """
        # set up subplots to add plots to
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                'Lottery Ball Distribution',
                'Powerball Distribution',
                'Money Spent vs Won',
                'Profit'
            ]
        )

        # create and add distribution graph for lotto balls chosen
        all_balls = self._get_all_balls()
        ball_dist = self._create_histogram(all_balls, name='Lottery Balls', histnorm='probability')
        fig.add_trace(ball_dist, row=1, col=1)

        # create and add distribution graph for powerballs chosen
        powerball_dist = self._create_histogram(self.chosen_powerball, name='Powerballs', histnorm='probability')
        fig.add_trace(powerball_dist, row=1, col=2)

        # create and add scatter plot for the cumulative money spent
        timeframe = [i for i in range(1, self.plays + 1)]
        spent = np.cumsum(self.spent)
        if len(spent) > max_points:
            x, y = self._smooth_fit(timeframe, spent, points=max_points)
        else:
            x, y = timeframe, spent
        cost_scatter = self._create_scatter(
            x=x,
            y=y,
            name='Money Spent'
        )
        fig.add_trace(cost_scatter, row=2, col=1)

        # create and add scatter plot for the cumulative money won
        # add to same row and col to combine graphs
        won = np.cumsum(self.winnings)
        if len(won) > max_points:
            x, y = self._smooth_fit(timeframe, won, points=max_points)
        else:
            x, y = timeframe, won
        won_scatter = self._create_scatter(
            x=x,
            y=y,
            name='Money Won'
        )
        fig.add_trace(won_scatter, row=2, col=1)

        # create and add waterfall graph for the cumulative profit
        profit = self._calc_profit()
        if len(profit) > max_points:
            x, y = self._smooth_fit(timeframe, profit, points=max_points)
            print(len(x), len(y), len(profit))
        else:
            x, y = timeframe, profit
        profit_waterfall = self._create_waterfall(
            x=x,
            y=y
        )
        fig.add_trace(profit_waterfall, row=2, col=2)

        # style subplot figure
        fig.update_layout(
            template='plotly_dark',
            showlegend=False
        )
        fig.show()


if __name__ == '__main__':
    sim = Lotto()
    sim.run(jackpot=250_000_000, add_powerplay=True, num_plays=1_000_000)
    sim.export_results('results.csv')
