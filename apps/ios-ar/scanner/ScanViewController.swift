import UIKit
import ARKit
import RealityKit

/// Root view controller for the LiDAR body scan capture flow.
/// Manages the ARSession lifecycle, drives the capture UI, and coordinates
/// point cloud accumulation and PLY export.
class ScanViewController: UIViewController {

    // MARK: - Properties

    private var arView: ARView!
    private var session: ARSession { arView.session }
    private let accumulator = PointCloudAccumulator()
    private let sessionManager = ScanSessionManager()

    private var captureButton: UIButton!
    private var statusLabel: UILabel!
    private var isCapturing = false

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupARView()
        setupUI()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        startARSession()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        session.pause()
    }

    // MARK: - AR Setup

    private func setupARView() {
        arView = ARView(frame: view.bounds, cameraMode: .ar, automaticallyConfigureSession: false)
        arView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(arView)
        arView.session.delegate = self
    }

    private func startARSession() {
        guard ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) else {
            showAlert(title: "LiDAR Required",
                      message: "This app requires an iPhone 12 Pro or later with LiDAR sensor.")
            return
        }
        let config = ARWorldTrackingConfiguration()
        config.sceneReconstruction = .meshWithClassification
        config.frameSemantics = [.sceneDepth, .smoothedSceneDepth]
        config.environmentTexturing = .none
        session.run(config, options: [.resetTracking, .removeExistingAnchors])
    }

    // MARK: - UI

    private func setupUI() {
        // Status label
        statusLabel = UILabel()
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        statusLabel.text = "Ready — press Scan to start"
        statusLabel.textColor = .white
        statusLabel.textAlignment = .center
        statusLabel.font = .systemFont(ofSize: 16, weight: .medium)
        view.addSubview(statusLabel)

        // Capture button
        captureButton = UIButton(type: .system)
        captureButton.translatesAutoresizingMaskIntoConstraints = false
        captureButton.setTitle("Start Scan", for: .normal)
        captureButton.titleLabel?.font = .systemFont(ofSize: 20, weight: .bold)
        captureButton.backgroundColor = UIColor.systemBlue
        captureButton.setTitleColor(.white, for: .normal)
        captureButton.layer.cornerRadius = 30
        captureButton.addTarget(self, action: #selector(toggleCapture), for: .touchUpInside)
        view.addSubview(captureButton)

        NSLayoutConstraint.activate([
            statusLabel.bottomAnchor.constraint(equalTo: captureButton.topAnchor, constant: -16),
            statusLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            statusLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            captureButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            captureButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -40),
            captureButton.widthAnchor.constraint(equalToConstant: 160),
            captureButton.heightAnchor.constraint(equalToConstant: 60)
        ])
    }

    // MARK: - Capture Control

    @objc private func toggleCapture() {
        if isCapturing {
            stopCapture()
        } else {
            startCapture()
        }
    }

    private func startCapture() {
        isCapturing = true
        accumulator.reset()
        sessionManager.beginSession()
        captureButton.setTitle("Stop & Export", for: .normal)
        captureButton.backgroundColor = .systemRed
        statusLabel.text = "Scanning… rotate slowly around subject"
    }

    private func stopCapture() {
        isCapturing = false
        sessionManager.endSession()
        captureButton.isEnabled = false
        statusLabel.text = "Processing \(accumulator.pointCount) points…"

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            let exporter = PointCloudExporter(accumulator: self.accumulator,
                                              scanID: self.sessionManager.scanID)
            do {
                let url = try exporter.exportPLY()
                let meta = try self.sessionManager.writeMetadata(pointCount: self.accumulator.pointCount, plyURL: url)
                DispatchQueue.main.async {
                    self.statusLabel.text = "Export complete ✓"
                    self.captureButton.isEnabled = true
                    self.captureButton.setTitle("Start Scan", for: .normal)
                    self.captureButton.backgroundColor = .systemBlue
                    self.presentShareSheet(for: [url, meta])
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusLabel.text = "Export failed: \(error.localizedDescription)"
                    self.captureButton.isEnabled = true
                }
            }
        }
    }

    private func presentShareSheet(for urls: [URL]) {
        let activity = UIActivityViewController(activityItems: urls, applicationActivities: nil)
        present(activity, animated: true)
    }

    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - ARSessionDelegate

extension ScanViewController: ARSessionDelegate {
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        guard isCapturing else { return }
        // Throttle: accumulate every 3rd frame to balance coverage vs memory
        guard sessionManager.shouldAccumulateFrame() else { return }
        accumulator.accumulate(frame: frame)
        DispatchQueue.main.async {
            self.statusLabel.text = "Scanning… \(self.accumulator.pointCount) pts"
        }
    }

    func session(_ session: ARSession, didFailWithError error: Error) {
        DispatchQueue.main.async {
            self.statusLabel.text = "Session error: \(error.localizedDescription)"
        }
    }
}
