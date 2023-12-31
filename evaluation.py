import json
from pathlib import Path
import interval
import os

OUTPUTDIR = 'stat_result'

SOURCE_DIR = 'inference_result_pose3d'

UR_FALL_INFERENCE = f"{SOURCE_DIR}/UR_FALL.json"
LE2I_INFERENCE = f"{SOURCE_DIR}/le2i.json"
# MULTI_CAM_INFERENCE = "inference_result/multi_cam.json"

MULTI_CAM_GROUND = "dataset/Multicam/ground_truth.json"
LE2I_HOME_GROUND = "dataset/Le2i_Fall_Detection_Dataset/home/Annotation_files"
LE2I_COFFEE_GROUND = "dataset/Le2i_Fall_Detection_Dataset/coffee_room/Annotation_files"


isExist = os.path.exists(OUTPUTDIR)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(OUTPUTDIR)

def read_first_two_line(file_path):
    file1 = open(file_path, 'r')
    Lines = file1.readlines()
    if Lines[0] == '0\n' and Lines[1] == '0\n':
        return 0
    else:
        return 1


class ModelResult:
    def __init__(self) -> None:
        self.total_n = 0
        self.true_pos = []
        self.true_neg = []
        self.false_pos = []
        self.false_neg = []
        pass

    def add_tp(self, vid_name):
        self.total_n += 1
        self.true_pos.append(vid_name)
        pass

    def add_tn(self, vid_name):
        self.total_n += 1
        self.true_neg.append(vid_name)
        pass

    def add_fp(self, vid_name):
        self.total_n += 1
        self.false_pos.append(vid_name)
        pass

    def add_fn(self, vid_name):
        self.total_n += 1
        self.false_neg.append(vid_name)
        pass

    def get_dict(self):
        precision = len(self.true_pos) / \
            (len(self.true_pos) + len(self.false_pos))
        recall = len(self.true_pos) / \
            (len(self.true_pos) + len(self.false_neg))
        f1_score = 2 * precision * recall / (precision + recall)

        return_result = {
            "score": {
                "total": self.total_n,
                "true_pos": len(self.true_pos),
                "true_neg": len(self.true_neg),
                "false_pos": len(self.false_pos),
                "false_neg": len(self.false_neg),
                "accuracy": len(self.true_pos) / (self.total_n),
                "precison": precision,
                "recall": recall,
                "f1_score": f1_score,
            },
            "file": {
                "true_pos": self.true_pos,
                "true_neg": self.true_neg,
                "false_pos": self.false_pos,
                "false_neg": self.false_neg,
            },
        }

        return return_result


def le2i(src, opt):
    result = ModelResult()

    file = open(f"{src}/le2i.json")
    inference_result = json.load(file)
    file.close()

    count = 0
    # for video in inference_result['coffee_room']:
    for video in inference_result['coffee_room']:
        for id in video:
            file_path = f'{LE2I_COFFEE_GROUND}/{id}'
            file_path = file_path.replace('.mp4', '.txt')
            if read_first_two_line(file_path) == 1:
                if 1 in video[id]:
                    # Fall in the video and the model output as yes
                    result.add_tp(f"coffee_room/{id}")
                else:
                    # Fall in the video and the model output as no
                    result.add_fn(f"coffee_room/{id}")
            else:
                if 1 in video[id]:
                    # Fall not in the video and the model output as yes
                    result.add_fp(f"coffee_room/{id}")
                else:
                    # Fall not in the video and the model output as no
                    result.add_tn(f"coffee_room/{id}")

    for video in inference_result['home']:
        for id in video:
            file_path = f'{LE2I_HOME_GROUND}/{id}'
            file_path = file_path.replace('.mp4', '.txt')
            if read_first_two_line(file_path) == 1:
                if 1 in video[id]:
                    # Fall in the video and the model output as yes
                    result.add_tp(f"home/{id}")
                else:
                    # Fall in the video and the model output as no
                    result.add_fn(f"home/{id}")
            else:
                if 1 in video[id]:
                    # Fall not in the video and the model output as yes
                    result.add_fp(f"home/{id}")
                else:
                    # Fall not in the video and the model output as no
                    result.add_tn(f"home/{id}")
    stat_data = result.get_dict()
    print(stat_data["score"])

    Path(opt).mkdir(parents=True, exist_ok=True)
    with open(f"{opt}/LE2I_EVAL.json", "w") as outfile:
        json.dump(stat_data, outfile, indent=4)

def get_sequence(ipt_list: list) -> list:
    result = ModelResult()

    file = open(UR_FALL_INFERENCE)
    inference_result = json.load(file)
    file.close()

    for video in inference_result['fall']:
        for id in video:
            if 1 in video[id]:
                # Fall in the video and the model output as yes
                result.add_tp(id)
            else:
                # Fall in the video and the model output as no
                result.add_fn(id)

    for video in inference_result['adl']:
        for id in video:
            if 1 in video[id]:
                # Fall not in the video and the model output as yes
                result.add_fp(id)
            else:
                # Fall not in the video and the model output as no
                result.add_tn(id)


def ur_fall(src, opt):
    result = ModelResult()

    file = open(f"{src}/UR_FALL.json")
    inference_result = json.load(file)
    file.close()

    for video in inference_result['fall']:
        for id in video:
            if 1 in video[id]:
                # Fall in the video and the model output as yes
                result.add_tp(id)
            else:
                # Fall in the video and the model output as no
                result.add_fn(id)

    for video in inference_result['adl']:
        for id in video:
            if 1 in video[id]:
                # Fall not in the video and the model output as yes
                result.add_fp(id)
            else:
                # Fall not in the video and the model output as no
                result.add_tn(id)


    stat_data = result.get_dict()
    print(stat_data["score"])

    Path(opt).mkdir(parents=True, exist_ok=True)
    with open(f"{opt}/UR_FALL_EVAL.json", "w") as outfile:
        json.dump(stat_data, outfile, indent=4)


def main():
    print("** ST-GCN **")
    # ur_fall("inference_result_stgcn", "stat_result/stgcn")
    le2i("inference_result_stgcn", "stat_result/stgcn")

    print("** AGCN **")
    # ur_fall("inference_result_AGCN", "stat_result/AGCN")
    le2i("inference_result_AGCN", "stat_result/AGCN")

    print("** Pose3d **")
    # ur_fall("inference_result_pose3d", "stat_result/pose3d")
    le2i("inference_result_pose3d", "stat_result/pose3d")

    print("** PlusPlus **")
    # ur_fall("inference_result_plusplus", "stat_result/plusplus")
    le2i("inference_result_plusplus", "stat_result/plusplus")

if __name__ == "__main__":
    main()



# def multicam():
#     '''
#     1: Walking, standing up
#     2: Falling
#     3: Lying on the ground
#     4: Crounching
#     5: Moving down
#     6: Moving up
#     7: Sitting
#     8: Lying on a sofa
#     9: Moving horizontaly
#     '''
#     result = ModelResult()

#     file = open(MULTI_CAM_INFERENCE)
#     inference_result = json.load(file)
#     file.close()

#     file = open(MULTI_CAM_GROUND)
#     ground_truth = json.load(file)
#     file.close()

#     for chute in inference_result:
#         print(chute)
#         for cam in inference_result[chute]:
#             print(f'{chute} {cam}')
#             fall_interval = get_sequence(inference_result[chute][cam])
#             # Find out all falling interval
#             drop_interval = []
#             for section in fall_interval:
#                 # print(interval.interval[section])
#                 for fall in ground_truth[chute]:
#                     if fall['code'] != 2:
#                         continue
#                     # print(interval.interval[fall['start'], fall['end']])
#                     if (interval.interval[fall['start'], fall['end']] & interval.interval[section]):
#                         result.add_tp(id)
#                         print(interval.interval[fall['start'], fall['end']], interval.interval[section])
#                         print('TRUE POSITIVE')
#                         drop_interval.append(section)
#                         return