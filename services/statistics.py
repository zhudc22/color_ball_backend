import pandas as pd


class LotteryStatistics:
    def __init__(self, dataframe):
        self.df = dataframe

    def calculate_fixed_interval_occurrences(self, start_period, interval):
        """
        需求一：计算指定期号之前的num_periods期内，每个数字出现的次数

        :param start_period: int, 开始期号
        :param interval: int, 间隔
        """
        period_data = self.df[
            (self.df["期号"] <= start_period)
            & (self.df["期号"] > start_period - interval)
        ].copy()

        occurrences = {f"q{i}": 0 for i in range(10)}
        for _, row in period_data.iterrows():
            seen = set()
            for val in row[1:]:
                if pd.notna(val) and val not in seen:
                    occurrences[f"q{int(val)}"] += 1
                    seen.add(val)

        return occurrences

    def calculate_multi_period_occurrences(self, start_period, num_periods, interval):
        """
        连续统计多期多次

        :param start_period: int, 开始期号
        :param num_periods: int, 期数
        :param interval: int, 间隔

        """
        results = []
        for i in range(num_periods):
            current_period = start_period - i * interval
            if current_period < 1:
                raise ValueError("开始期号或间隔设置错误，计算的期号小于1")
            occurrences = self.calculate_fixed_interval_occurrences(
                current_period, interval
            )
            results.append((occurrences, current_period))
        return results

    @staticmethod
    def create_calculate_occurrences_table(occurrences, next_numbers, start_period):
        """
        构造展示表格

        :param occurrences: dict, 每个数字出现的次数
        :param next_numbers: list, 下一期的数字
        :param start_period: int, 开始期号

        """
        max_count = max(occurrences.values())
        data = {f"{i}次": [] for i in range(max_count + 1)}
        for key, count in occurrences.items():
            data[f"{count}次"].append(
                key + ("$" if int(key[1:]) in next_numbers else "")
            )

        # Adjust list lengths
        max_len = max(len(lst) for lst in data.values())
        for key in data:
            data[key] += [""] * (max_len - len(data[key]))

        data["期号"] = [f"{start_period}期"] + [""] * (max_len - 1)
        return pd.DataFrame(data)

    @staticmethod
    def create_multi_period_table(multi_period_data):
        """
        创建显示表

        :param multi_period_data: list, 多期多次数据
        """
        data = {f"{i}次": [] for i in range(11)}
        data["期号"] = []
        for occurrences, period in multi_period_data:
            row = {f"{i}次": "" for i in range(11)}
            for key, count in occurrences.items():
                row[f"{count}次"] += key + ", "
            for i in range(11):
                if row[f"{i}次"]:
                    row[f"{i}次"] = row[f"{i}次"][:-2]
            data["期号"].append(f"{period}期")
            for i in range(11):
                data[f"{i}次"].append(row[f"{i}次"])
        return pd.DataFrame(data)

    def calculate_heatmap(self, start_period, num_periods, num_iterations):
        """
        需求二：
        计算热力图数据
        :param start_period: int, 开始期号
        :param num_periods: int, 间隔期数
        :param num_iterations: int, 连续统计次数
        """
        if start_period <= 0 or num_iterations <= 0 or num_periods <= 0:
            raise ValueError("开始期号、后退期数和间隔必须大于0")

        if start_period - num_periods * num_iterations < 1:
            raise ValueError("计算范围超出了可用数据范围，请减小后退期数或间隔")

        results = {f"q{i}": [] for i in range(10)}
        for i in range(num_iterations):
            current_period = start_period - i * num_periods
            if current_period < 1:
                raise ValueError("开始期号或间隔设置错误，计算的期号小于1")
            occurrences = self.calculate_fixed_interval_occurrences(
                current_period, num_periods
            )
            for key in results.keys():
                results[key].append(occurrences[key] / num_periods)

        periods = range(
            start_period - num_periods * num_iterations + 1,
            start_period + 1,
            num_periods,
        )
        return results, periods

    def calculate_occurrences_by_multipliers(
        self, start_period, base_interval, num_multipliers
    ):
        """
        需求三
        计算多个倍数的数据
        :param start_period:
        :param base_interval:
        :param num_multipliers:
        :return:
        """
        results = []
        for multiplier in range(1, num_multipliers + 1):
            current_interval = base_interval * multiplier
            occurrences = self.calculate_fixed_interval_occurrences(
                start_period, current_interval
            )
            results.append((occurrences, current_interval))
        return results

    @staticmethod
    def create_multipliers_display_table(multi_period_data, next_numbers):
        """
        根据数据中的出现次数动态构造显示表格。
        """
        # 在所有计算中找到最大的出现次数
        max_count = max(
            max(occurrences.values())
            for occurrences, _ in multi_period_data
            if occurrences
        )

        # 根据最大次数动态创建字典键
        data = {f"{i}次": [] for i in range(max_count + 1)}
        data["间隔"] = []

        for occurrences, interval in multi_period_data:
            row = {
                f"{i}次": [] for i in range(max_count + 1)
            }  # 确保每一行都有所有可能的键
            for key, count in occurrences.items():
                mark = "$" if int(key[1:]) in next_numbers else ""
                row[f"{count}次"].append(key + mark)
            for i in range(max_count + 1):
                row[f"{i}次"] = ", ".join(row[f"{i}次"]) if row[f"{i}次"] else ""
            data["间隔"].append(f"{interval}期间隔")
            for i in range(max_count + 1):
                data[f"{i}次"].append(row[f"{i}次"])
        return pd.DataFrame(data)

    def calculate_accumulative_intervals_occurrences(self, start_period, num_intervals):
        """
        需求四
        计算累积间隔的数据
        :param start_period:
        :param num_intervals:
        :return:
        """
        results = {f"q{i}": [] for i in range(10)}
        for interval in range(1, num_intervals + 1):
            occurrences = self.calculate_fixed_interval_occurrences(
                start_period, interval
            )
            for key in results.keys():
                results[key].append(occurrences[key] / interval)
        return results


if __name__ == "__main__":
    from data_manager_server import (
        read_data,
        plot_heatmap,
        plot_heatmaps_fourth_requirement,
    )

    data_path = "../data/数据库1.xlsx"
    df = read_data(data_path)

    lottery_stats = LotteryStatistics(df)
    start_period = 40
    num_periods = 5
    interval = 5

    try:
        # 需求一
        calculate_occurrences = lottery_stats.calculate_fixed_interval_occurrences(
            start_period, num_periods
        )
        try:
            next_period_numbers_data = (
                df.loc[df["期号"] == start_period + 1, df.columns[1:]]
                .dropna(axis=1)
                .values
            )
            if next_period_numbers_data.size > 0:
                next_period_numbers = next_period_numbers_data.astype(int).tolist()[0]
            else:
                next_period_numbers = []
        except IndexError:
            print("下一期数据不可用，检查期号是否正确。")
            next_period_numbers = []

        display_table = lottery_stats.create_calculate_occurrences_table(
            calculate_occurrences, next_period_numbers, start_period
        )
        print(display_table)
        display_table.to_csv(r"../data/occurrences.csv", index=False)

        multi_period_data = lottery_stats.calculate_multi_period_occurrences(
            start_period, num_periods, interval
        )
        display_table = lottery_stats.create_multi_period_table(multi_period_data)
        print(display_table)
        display_table.to_csv(r"../data/multi_output.csv", index=False)

        # 需求二
        # 计算数据
        heatmap_data, periods = lottery_stats.calculate_heatmap(
            start_period, num_periods, interval
        )
        # 绘图
        plot_heatmap(heatmap_data, periods)

        # 需求三
        num_multipliers = 5
        multipliers_data = lottery_stats.calculate_occurrences_by_multipliers(
            start_period, interval, num_multipliers
        )
        display_table = lottery_stats.create_multipliers_display_table(
            multipliers_data, next_period_numbers
        )
        print(display_table)
        display_table.to_csv(r"../data/multipliers_output.csv", index=False)

        # 需求四
        rates = lottery_stats.calculate_accumulative_intervals_occurrences(
            start_period, interval
        )
        plot_heatmaps_fourth_requirement(rates, interval)

    except ValueError as e:
        print(f"输入参数错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
