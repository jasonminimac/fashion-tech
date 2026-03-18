import ARKit
import simd

/// JointLogger
/// Iterates all 91 joints in an ARBodyAnchor's skeleton and logs positions to console.
///
/// Output format:
///   [JOINT] frame=N joint=left_hand_joint x=0.123 y=0.456 z=0.789
///
/// Joint positions are in body-local space (relative to body anchor transform).
/// To get world-space positions, apply bodyAnchor.transform to each joint transform.

enum JointLogger {

    // MARK: - Public API

    /// Log all joints from a body anchor.
    /// - Parameters:
    ///   - bodyAnchor: The ARBodyAnchor received from the session.
    ///   - frameIndex: Current frame number for log correlation.
    ///   - worldSpace: If true, transforms joint positions into world space using bodyAnchor.transform.
    static func log(bodyAnchor: ARBodyAnchor, frameIndex: Int, worldSpace: Bool = false) {
        let skeleton = bodyAnchor.skeleton
        let definition = ARSkeletonDefinition.defaultBody3D
        let jointNames = definition.jointNames  // 91 entries

        // Body anchor's world transform (bodyLocal → world)
        let bodyTransform = bodyAnchor.transform

        for (index, name) in jointNames.enumerated() {
            // jointModelTransforms: body-local space (relative to body anchor origin)
            let localTransform = skeleton.jointModelTransforms[index]

            let position: SIMD3<Float>
            if worldSpace {
                let worldTransform = bodyTransform * localTransform
                position = simd_make_float3(worldTransform.columns.3)
            } else {
                position = simd_make_float3(localTransform.columns.3)
            }

            printJoint(frame: frameIndex, name: name, position: position)
        }
    }

    /// Log a single named joint (convenience for debugging specific joints).
    static func logJoint(named jointName: String, bodyAnchor: ARBodyAnchor, frameIndex: Int) {
        let definition = ARSkeletonDefinition.defaultBody3D
        guard let index = definition.jointNames.firstIndex(of: jointName) else {
            print("[JOINT-WARN] Unknown joint: \(jointName)")
            return
        }
        let transform = bodyAnchor.skeleton.jointModelTransforms[index]
        let position = simd_make_float3(transform.columns.3)
        printJoint(frame: frameIndex, name: jointName, position: position)
    }

    // MARK: - All 91 Joint Names (Reference)
    //
    // These come from ARSkeletonDefinition.defaultBody3D.jointNames at runtime.
    // Listed here for reference and validation.
    //
    // Root & spine:
    //   root, hips_joint, spine_1_joint ... spine_7_joint
    //
    // Head & neck:
    //   neck_1_joint ... neck_4_joint, head_joint, jaw_joint, chin_joint
    //   left_eye_joint, right_eye_joint, left_eye_lowerLid_joint, right_eye_lowerLid_joint
    //   left_eye_upperLid_joint, right_eye_upperLid_joint
    //   left_eyeball_joint, right_eyeball_joint
    //   nose_joint
    //
    // Left arm:
    //   left_shoulder_1_joint, left_arm_joint, left_forearm_joint, left_hand_joint
    //
    // Left hand fingers (×5, each has joint_1..joint_3 + tip):
    //   left_handThumbStart_joint, left_handThumb_1_joint, left_handThumb_2_joint, left_handThumbEnd_joint
    //   left_handIndexStart_joint, left_handIndex_1_joint ... left_handIndexEnd_joint
    //   left_handMidStart_joint, left_handMid_1_joint ... left_handMidEnd_joint
    //   left_handRingStart_joint, left_handRing_1_joint ... left_handRingEnd_joint
    //   left_handPinkyStart_joint, left_handPinky_1_joint ... left_handPinkyEnd_joint
    //
    // Right arm (mirror of left):
    //   right_shoulder_1_joint, right_arm_joint, right_forearm_joint, right_hand_joint
    //   right_hand* (same structure as left)
    //
    // Left leg:
    //   left_upLeg_joint, left_leg_joint, left_foot_joint, left_toes_joint, left_toesEnd_joint
    //
    // Right leg (mirror):
    //   right_upLeg_joint, right_leg_joint, right_foot_joint, right_toes_joint, right_toesEnd_joint

    // MARK: - Private

    private static func printJoint(frame: Int, name: String, position: SIMD3<Float>) {
        // Format to 3 decimal places — sufficient for body tracking resolution
        print(String(format: "[JOINT] frame=%d joint=%@ x=%.3f y=%.3f z=%.3f",
                     frame, name, position.x, position.y, position.z))
    }
}

// MARK: - simd helpers

private func simd_make_float3(_ col: SIMD4<Float>) -> SIMD3<Float> {
    return SIMD3<Float>(col.x, col.y, col.z)
}
