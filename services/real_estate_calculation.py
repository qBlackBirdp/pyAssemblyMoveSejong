# real_estate_calculation.py

def calculate_quarterly_average(data, quarter):
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    quarter_data = [entry['DTA_VAL'] for entry in data if
                    start_month <= int(entry['WRTTIME_DESC'].split("년")[1].split("월")[0]) <= end_month]

    if quarter_data:
        return sum(quarter_data) / len(quarter_data)
    else:
        return None


def calculate_quarterly_change_rate(previous_quarter_avg, current_quarter_avg):
    if previous_quarter_avg == 0:
        return None
    else:
        return ((current_quarter_avg - previous_quarter_avg) / previous_quarter_avg) * 100


def calculate_sequential_change(data):
    if isinstance(data, dict):
        data = data.get("row", [])
    elif not isinstance(data, list):
        raise ValueError("Expected data to be a list or a dictionary with a 'row' key")

    # 모든 데이터를 연도별/분기별로 그룹화
    def group_by_quarter(data):
        grouped_data = {}
        for entry in data:
            year, month = entry["WRTTIME_DESC"].split("년")
            year = int(year.strip())
            month = int(month.replace("월", "").strip())

            # 분기 계산
            quarter = (month - 1) // 3 + 1
            key = (year, quarter)  # (연도, 분기)
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(entry["DTA_VAL"])
        return grouped_data

    grouped_data = group_by_quarter(data)

    # 분기별 평균 계산
    def calculate_quarterly_averages(grouped_data):
        averages = {}
        for (year, quarter), values in grouped_data.items():
            averages[(year, quarter)] = sum(values) / len(values)
        return averages

    averages = calculate_quarterly_averages(grouped_data)

    # 연도/분기별 변동률 계산
    sorted_keys = sorted(averages.keys())
    change_rates = {}

    for i in range(1, len(sorted_keys)):
        current_key = sorted_keys[i]
        previous_key = sorted_keys[i - 1]

        current_avg = averages[current_key]
        previous_avg = averages[previous_key]

        if previous_avg is not None and current_avg is not None:
            change_rate = ((current_avg - previous_avg) / previous_avg) * 100
        else:
            change_rate = None

        change_rates[f"{current_key[0]}-Q{current_key[1]}"] = {
            "Current Avg": current_avg,
            "Previous Avg": previous_avg,
            "Change Rate": change_rate
        }

    return change_rates
