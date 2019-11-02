import json


def get_new_series():
    try:
        with open('./series.json', 'r') as f:
            text = f.read()
            data = json.loads(text)['data']
            f.close()
    except:
        print('No data found.')
    return data


def main():
    data = 0
    try:
        data = get_new_series()
    except:
        print('No data found.')

    if data:
        for series in data:
            print('Name: {0}'.format(series['name']))
            print('New Episode number: {0}'.format(
                series['latest_episode_num']-series['new_epi_count']+1))
            print("New Episodes: {0}".format(series['new_epi_count']))
            print('Episode link: {0}'.format(series['latest_episode_link']))
            print("\n")
    input('Press any key to continue.')


if __name__ == '__main__':
    main()
