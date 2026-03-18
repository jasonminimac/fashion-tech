import UIKit
import ARKit
import SceneKit

/// BodyTrackingViewController
/// Sets up an ARSession with ARBodyTrackingConfiguration, receives body anchor
/// updates, and delegates joint logging to JointLogger.
///
/// Requirements:
/// - iPhone 12 or later (iOS 14+)
/// - NSCameraUsageDescription in Info.plist
/// - Physical device required (simulator does NOT support ARBodyTrackingConfiguration)

class BodyTrackingViewController: UIViewController {

    // MARK: - Properties

    private var sceneView: ARSCNView!
    private var frameCounter: Int = 0

    // FPS tracking
    private var lastTimestamp: TimeInterval = 0
    private var frameCount: Int = 0
    private var fpsDisplayTimer: Timer?

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupSceneView()
        checkDeviceSupport()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        startARSession()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        sceneView.session.pause()
        fpsDisplayTimer?.invalidate()
    }

    // MARK: - Setup

    private func setupSceneView() {
        sceneView = ARSCNView(frame: view.bounds)
        sceneView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        sceneView.delegate = self
        sceneView.session.delegate = self
        sceneView.showsStatistics = true   // shows fps overlay in debug builds
        sceneView.automaticallyUpdatesLighting = true
        view.addSubview(sceneView)

        // Lightweight scene — we're logging, not rendering garments yet
        let scene = SCNScene()
        sceneView.scene = scene
    }

    private func checkDeviceSupport() {
        guard ARBodyTrackingConfiguration.isSupported else {
            let alert = UIAlertController(
                title: "Body Tracking Unsupported",
                message: "ARBodyTrackingConfiguration requires iPhone 12 or later running iOS 14+.",
                preferredStyle: .alert
            )
            alert.addAction(UIAlertAction(title: "OK", style: .default))
            present(alert, animated: true)
            print("[AR-ERROR] ARBodyTrackingConfiguration is not supported on this device.")
            return
        }
        print("[AR-INFO] Body tracking supported. Starting session.")
    }

    // MARK: - AR Session

    private func startARSession() {
        guard ARBodyTrackingConfiguration.isSupported else { return }

        let configuration = ARBodyTrackingConfiguration()

        // Use highest available fps format
        if let highFpsFormat = ARBodyTrackingConfiguration.supportedVideoFormats
            .filter({ $0.framesPerSecond >= 60 }).first {
            configuration.videoFormat = highFpsFormat
            print("[AR-INFO] Using \(highFpsFormat.framesPerSecond)fps video format.")
        } else {
            print("[AR-INFO] Using default video format.")
        }

        sceneView.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
        startFPSMonitor()
    }

    // MARK: - FPS Monitor

    private func startFPSMonitor() {
        fpsDisplayTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            print("[AR-PERF] fps=\(self.frameCount)")
            self.frameCount = 0
        }
    }
}

// MARK: - ARSCNViewDelegate

extension BodyTrackingViewController: ARSCNViewDelegate {

    func renderer(_ renderer: SCNSceneRenderer, updateAtTime time: TimeInterval) {
        frameCount += 1
        frameCounter += 1
    }
}

// MARK: - ARSessionDelegate

extension BodyTrackingViewController: ARSessionDelegate {

    func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        let currentFrame = frameCounter

        for anchor in anchors {
            guard let bodyAnchor = anchor as? ARBodyAnchor else { continue }

            // Only log if tracking state is good
            guard bodyAnchor.isTracked else {
                print("[AR-WARN] frame=\(currentFrame) body anchor not fully tracked")
                continue
            }

            JointLogger.log(bodyAnchor: bodyAnchor, frameIndex: currentFrame)
        }
    }

    func session(_ session: ARSession, didFailWithError error: Error) {
        print("[AR-ERROR] Session failed: \(error.localizedDescription)")
    }

    func sessionWasInterrupted(_ session: ARSession) {
        print("[AR-WARN] Session interrupted.")
    }

    func sessionInterruptionEnded(_ session: ARSession) {
        print("[AR-INFO] Session interruption ended. Restarting.")
        startARSession()
    }
}
