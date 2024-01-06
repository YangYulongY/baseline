import os
import pandas as pd
import numpy as np
import math

# Ranking: 1
# Name: Type_of_action
# Description: Mouse Movement, Point Click, or Drag and Drop
def type_of_action(row):
    if row['state'] == 'Move' and row['button'] == 'NoButton':
        return 'Mouse Movement'
    elif (row['state'] == 'Pressed' or row['state'] == 'Released') and row['button'] != 'NoButton':
        return 'Point Click'
    elif row['state'] == 'Drag':
        return 'Drag and Drop'
    else:
        return 'Unknown'

# Ranking 2
# Name: Travelled_distance_in pixels
# Description: The frequency of actions within different distance ranges
def calculate_distance(row, prev_row):
    if row['state'] == 'Move':
        return np.sqrt((row['x'] - prev_row['x'])**2 + (row['y'] - prev_row['y'])**2)
    else:
        return 0

# Ranking 3
# Name: Elapsed_time
# Description: Elapsed time from the start of the session recorded by the network monitoring device
def calculate_elapsed_time(row, prev_row):
    return row['client timestamp'] - prev_row['client timestamp']

# Ranking 4
# Name: Direction of movement
# Description: Direction of end to end line
def calculate_direction(row, prev_row):
    dx = row['x'] - prev_row['x']
    dy = row['y'] - prev_row['y']
    angle = np.arctan2(dy, dx)
    angle_degrees = np.degrees(angle)
    return angle_degrees

# Ranking 5
# Name: Straightness
# Description: The ratio between two endpoints of action and the length of the trajectory
def straight_line_distance(row, prev_row):
    return np.sqrt((row['x'] - prev_row['x'])**2 + (row['y'] - prev_row['y'])**2)

def calculate_straightness(row, prev_row, total_distance):
    line_distance = straight_line_distance(row, prev_row)
    if line_distance == 0:
        return 1
    return line_distance / total_distance

# Ranking 6
# Name: Num_points
# Description: Number of mouse events contained in an action
def generate_action_id(data):
    action_id = 0
    ids = [action_id]
    for i in range(1, len(data)):
        if data.iloc[i]['state'] != data.iloc[i-1]['state']:
            action_id += 1
        ids.append(action_id)
    return ids

def calculate_num_points(group):
    return len(group)

# Ranking 7
# Name: Sum_of_angles
# Description: How many angles in each action
def calculate_angle(x1, y1, x2, y2):
    return np.arctan2(y2 - y1, x2 - x1)

def calculate_sum_of_angles(group):
    if len(group) < 2:
        return 0
    angles = group.apply(lambda row: calculate_angle(row['x'], row['y'], row['next_x'], row['next_y']), axis=1)
    angle_diffs = np.abs(np.diff(angles))
    return np.sum(angle_diffs)

# Ranking 8
# Name: Mean_curv
# Description: Average of angle change and the travelled distance
def calculate_curvature(x1, y1, x2, y2, x3, y3):
    a = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    b = np.sqrt((x3 - x2)**2 + (y3 - y2)**2)
    c = np.sqrt((x3 - x1)**2 + (y3 - y1)**2)
    if a * b == 0: 
        return 0
    cosine_angle = (a**2 + b**2 - c**2) / (2 * a * b)
    cosine_angle = np.clip(cosine_angle, -1, 1)
    angle = np.arccos(cosine_angle)
    curvature = angle / min(a, b)
    return curvature

def calculate_mean_curvature(group):
    if len(group) < 3:
        return 0
    curvatures = []
    for i in range(1, len(group)-1):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        x3, y3 = group.iloc[i+1]['x'], group.iloc[i+1]['y']
        curvatures.append(calculate_curvature(x1, y1, x2, y2, x3, y3))
    return np.mean(curvatures)

# Ranking 9
# Name: Sd_curv
# Description: Standard deviation between angle change and the trav-elled distance
def calculate_sd_curvature(group):
    if len(group) < 3:
        return 0
    curvatures = []
    for i in range(1, len(group)-1):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        x3, y3 = group.iloc[i+1]['x'], group.iloc[i+1]['y']
        curvatures.append(calculate_curvature(x1, y1, x2, y2, x3, y3))
    return np.std(curvatures)

# Ranking 10
# Name: Max_curv
# Description: Maximal values between angle change and the travelled distance
def calculate_max_curvature(group):
    if len(group) < 3:
        return 0
    curvatures = []
    for i in range(1, len(group)-1):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        x3, y3 = group.iloc[i+1]['x'], group.iloc[i+1]['y']
        curvatures.append(calculate_curvature(x1, y1, x2, y2, x3, y3))
    return max(curvatures)

# Ranking 11
# Name: Min_curv
# Description: Minimal values between angle change and the travelled distance
def calculate_min_curvature(group):
    if len(group) < 3:
        return 0
    curvatures = []
    for i in range(1, len(group)-1):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        x3, y3 = group.iloc[i+1]['x'], group.iloc[i+1]['y']
        curvatures.append(calculate_curvature(x1, y1, x2, y2, x3, y3))
    return min(curvatures)

# Ranking 12
# Name: Mean_omega
# Description: Average of angular velocity
def calculate_angular_velocity(x1, y1, x2, y2, time_diff):
    if time_diff == 0:
        return 0
    angle_change = calculate_angle(x1, y1, x2, y2)
    angular_velocity = angle_change / time_diff
    return angular_velocity

def calculate_mean_omega(group):
    if len(group) < 2:
        return 0
    angular_velocities = []
    for i in range(1, len(group)):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        time_diff = group.iloc[i]['client timestamp'] - group.iloc[i-1]['client timestamp']
        angular_velocities.append(calculate_angular_velocity(x1, y1, x2, y2, time_diff))
    return np.mean(angular_velocities)

# Ranking 13
# Name: Sd_omega
# Description: standard deviation of angular velocity
def calculate_sd_omega(group):
    if len(group) < 2:
        return 0
    angular_velocities = []
    for i in range(1, len(group)):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        time_diff = group.iloc[i]['client timestamp'] - group.iloc[i-1]['client timestamp']
        angular_velocity = calculate_angular_velocity(x1, y1, x2, y2, time_diff)
        angular_velocities.append(angular_velocity)
    return np.std(angular_velocities)

# Ranking 14
# Name: Max_ omega
# Description: maximal values of angular velocity
def calculate_max_omega(group):
    if len(group) < 2:
        return 0
    angular_velocities = []
    for i in range(1, len(group)):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        time_diff = group.iloc[i]['client timestamp'] - group.iloc[i-1]['client timestamp']
        angular_velocity = calculate_angular_velocity(x1, y1, x2, y2, time_diff)
        angular_velocities.append(angular_velocity)
    return max(angular_velocities)

# Ranking 15
# Name: Min_omega
# Description: minimal values of angular velocity
def calculate_min_omega(group):
    if len(group) < 2:
        return 0
    angular_velocities = []
    for i in range(1, len(group)):
        x1, y1 = group.iloc[i-1]['x'], group.iloc[i-1]['y']
        x2, y2 = group.iloc[i]['x'], group.iloc[i]['y']
        time_diff = group.iloc[i]['client timestamp'] - group.iloc[i-1]['client timestamp']
        angular_velocity = calculate_angular_velocity(x1, y1, x2, y2, time_diff)
        angular_velocities.append(angular_velocity)
    return min(angular_velocities)

def extract_features(data):
    # Ranking 1
    data['Type_of_action'] = data.apply(type_of_action, axis=1)    

    # Ranking 2
    distances = [0]
    for i in range(1, len(data)):
        distance = calculate_distance(data.iloc[i], data.iloc[i-1])
        distances.append(distance)
    data['Travelled_distance_in_pixels'] = distances

    # Ranking 3
    elapsed_times = [0]
    for i in range(1, len(data)):
        elapsed_time = calculate_elapsed_time(data.iloc[i], data.iloc[i-1])
        elapsed_times.append(elapsed_time)
    data['Elapsed_time'] = elapsed_times

    # Ranking 4
    directions = [0]
    for i in range(1, len(data)):
        direction = calculate_direction(data.iloc[i], data.iloc[i-1])
        directions.append(direction)
    data['Direction_of_movement'] = directions

    # Ranking 5
    straightness_values = [1]
    total_distance = 0
    for i in range(1, len(data)):
        total_distance += straight_line_distance(data.iloc[i], data.iloc[i-1])
        straightness = calculate_straightness(data.iloc[i], data.iloc[i-1], total_distance)
        straightness_values.append(straightness)
    data['Straightness'] = straightness_values

    # Ranking 6
    data['action_id'] = generate_action_id(data)
    num_points = data.groupby('action_id').apply(calculate_num_points)
    data['Num_points'] = data['action_id'].map(num_points)

    # Ranking 7
    data['next_x'] = data['x'].shift(-1)
    data['next_y'] = data['y'].shift(-1)
    sum_of_angles = data.groupby('action_id').apply(calculate_sum_of_angles)
    data['Sum_of_angles'] = data['action_id'].map(sum_of_angles)

    # Ranking 8
    mean_curvatures = data.groupby('action_id').apply(calculate_mean_curvature)
    data['Mean_curv'] = data['action_id'].map(mean_curvatures)

    # Ranking 9
    sd_curvatures = data.groupby('action_id').apply(calculate_sd_curvature)
    data['Sd_curv'] = data['action_id'].map(sd_curvatures)

    # Ranking 10
    max_curvatures = data.groupby('action_id').apply(calculate_max_curvature)
    data['Max_curv'] = data['action_id'].map(max_curvatures)

    # Ranking 11
    min_curvatures = data.groupby('action_id').apply(calculate_min_curvature)
    data['Min_curv'] = data['action_id'].map(min_curvatures)

    # Ranking 12
    mean_omegas = data.groupby('action_id').apply(calculate_mean_omega)
    data['Mean_omega'] = data['action_id'].map(mean_omegas)

    # Ranking 13
    sd_omegas = data.groupby('action_id').apply(calculate_sd_omega)
    data['Sd_omega'] = data['action_id'].map(sd_omegas)

    # Ranking 14
    max_omegas = data.groupby('action_id').apply(calculate_max_omega)
    data['Max_omega'] = data['action_id'].map(max_omegas)

    # Ranking 15
    min_omegas = data.groupby('action_id').apply(calculate_min_omega)
    data['Min_omega'] = data['action_id'].map(min_omegas)

    data.drop(columns=['record timestamp', 'client timestamp', 'button', 'state', 'x', 'y', 'action_id','next_x', 'next_y'], inplace = True)
    return data

# data = pd.read_csv('/Users/yangyulong/Documents/baseline/training_files/user7/session_0041905381', header=0)
labels_df = pd.read_csv('/Users/yangyulong/Documents/baseline/public_labels.csv', index_col='filename')

all_data = pd.DataFrame()
for root, dirs, files in os.walk('/Users/yangyulong/Documents/baseline/test_files/user7'):
    for file in files:
        # if file.startswith('session_'):
        #     session_data = pd.read_csv(os.path.join(root, file), header=0)

        #     session_data = extract_features(session_data)

        #     session_data['label'] = 0
            
        #     all_data = pd.concat([all_data, session_data], ignore_index=True)
        session_id = file.split('.')[0]
        if session_id in labels_df.index:
            session_data = pd.read_csv(os.path.join(root, file), header=0)
            session_data = extract_features(session_data)
            session_data['label'] = labels_df.loc[session_id, 'is_illegal']
            all_data = pd.concat([all_data, session_data], ignore_index=True)
        else:
            print(f"Label for {session_id} not found in public_labels.csv.")

all_data.to_csv('/Users/yangyulong/Documents/baseline/user7_final_test_dataset_with_labels.csv', index=False)
print("Data processing completed.")

print(all_data)