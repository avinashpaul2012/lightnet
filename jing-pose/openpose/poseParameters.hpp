#ifndef OPENPOSE_POSE_POSE_PARAMETERS_HPP
#define OPENPOSE_POSE_POSE_PARAMETERS_HPP

#include <map>
#include <vector>
#include "enumClasses.hpp"

#define OP_API

namespace op
{
    // Constant Global Parameters
    // For OpenCL-NMS in Ubuntu, (POSE_MAX_PEOPLE+1)*3(x,y,score) must be divisible by 32. Easy fix:
    // POSE_MAX_PEOPLE = 32n - 1
    // For OpenCL-NMS in Windows, it must be by 64, so 64n - 1
    const auto POSE_MAX_PEOPLE = 127u;

    // Model functions
    OP_API const std::map<unsigned int, std::string>& getPoseBodyPartMapping(const PoseModel poseModel);
    OP_API const std::string& getPoseProtoTxt(const PoseModel poseModel);
    OP_API const std::string& getPoseTrainedModel(const PoseModel poseModel);
    OP_API unsigned int getPoseNumberBodyParts(const PoseModel poseModel);
    OP_API const std::vector<unsigned int>& getPosePartPairs(const PoseModel poseModel);
    OP_API const std::vector<unsigned int>& getPoseMapIndex(const PoseModel poseModel);
    OP_API unsigned int getPoseMaxPeaks(const PoseModel poseModel);
    OP_API float getPoseNetDecreaseFactor(const PoseModel poseModel);
    OP_API unsigned int poseBodyPartMapStringToKey(const PoseModel poseModel, const std::string& string);
    OP_API unsigned int poseBodyPartMapStringToKey(const PoseModel poseModel, const std::vector<std::string>& strings);

    // Default NSM and body connector parameters
    OP_API float getPoseDefaultNmsThreshold(const PoseModel poseModel);
    OP_API float getPoseDefaultConnectInterMinAboveThreshold(const PoseModel poseModel);
    OP_API float getPoseDefaultConnectInterThreshold(const PoseModel poseModel);
    OP_API unsigned int getPoseDefaultMinSubsetCnt(const PoseModel poseModel);
    OP_API float getPoseDefaultConnectMinSubsetScore(const PoseModel poseModel);

    // const bool COCO_CHALLENGE = true;
    const bool COCO_CHALLENGE = false;
}

#endif // OPENPOSE_POSE_POSE_PARAMETERS_HPP
