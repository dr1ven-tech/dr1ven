//
//  ViewController.swift
//  Stereoscopic
//
//  Created by Matthieu Rouif on 09/10/2018.
//  Copyright © 2018 Dr1ve. All rights reserved.
//

import UIKit
import AVFoundation
import CoreLocation

class ViewController: UIViewController, AVCaptureFileOutputRecordingDelegate, AVCaptureVideoDataOutputSampleBufferDelegate, AVCaptureDepthDataOutputDelegate {

    @IBOutlet weak var videoView: UIView!
    
    enum CameraError: Error {
        case noCaptureDevice
        case cannotAddVideoOutput
    }

    fileprivate enum SessionSetupResult {
        case success
        case notAuthorized
        case configurationFailed(error: Error)
        
        var isSuccess: Bool {
            switch self {
            case .success: return true
            case .notAuthorized, .configurationFailed(error: _): return false
            }
        }
    }
    
    private enum RecordState {
        case loading
        case ready
        case recording
        case saving
    }

    private var cameraConfig: CameraConfig = .teleCamera {
        didSet {
            //if cameraConfig is set, reload everything
        }
    }
    
    private var setupResult: SessionSetupResult = .success {
        didSet {
            switch setupResult {
            case .configurationFailed(let error):
                let alert = UIAlertController(title: "error", message: error.localizedDescription, preferredStyle: .alert)
                self.show(alert, sender: nil)
            case .success:
                print("success")
            case .notAuthorized:
                print("not authorized")
            }
        }
    }
    
    private let session = AVCaptureSession()
    private var isSessionRunning = false
    private var recordState: RecordState = .loading
    private var teleDevice: AVCaptureDevice!
    private var videoDeviceInput: AVCaptureDeviceInput!
    private var statusBarOrientation: UIInterfaceOrientation = .landscapeRight
    private var videoOutputURL: URL!
    private var dataOutputURL: URL!

    private var startDate: Date!
    private var movieFileOutput = AVCaptureMovieFileOutput()
    // Communicate with the session and other session objects on this queue.
    private let sessionQueue = DispatchQueue(label: "session queue", attributes: [], autoreleaseFrequency: .workItem)
    
    private var videoMetadata: VideoMetadata?

    private let videoDataOutput = AVCaptureVideoDataOutput()
    private let dataOutputQueue = DispatchQueue(label: "video data queue", qos: .userInitiated, attributes: [], autoreleaseFrequency: .workItem)
    
    @IBOutlet weak var recordButton: UIButton!
    @IBOutlet weak var recordLabel: UILabel!
    @IBOutlet weak var cameraConfigButton: UIButton!
    
    // MARK: - View Controller Life Cycle

    override func viewDidLoad() {
        super.viewDidLoad()
        checkAuthorization()
        sessionQueue.async {
            self.configureSession()
        }
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        updateUI()
        let interfaceOrientation = UIApplication.shared.statusBarOrientation
        statusBarOrientation = interfaceOrientation
    }
    
    // MARK: - Authorization

    func checkAuthorization () {
        checkVideoAuthorization()
    }

    func checkVideoAuthorization() {
        // Check video authorization status, video access is required
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            // The user has previously granted access to the camera
            break
            
        case .notDetermined:
            /*
             The user has not yet been presented with the option to grant video access
             We suspend the session queue to delay session setup until the access request has completed
             */
            sessionQueue.suspend()
            AVCaptureDevice.requestAccess(for: .video, completionHandler: { granted in
                if !granted {
                    self.setupResult = .notAuthorized
                }
                self.sessionQueue.resume()
            })
            
        default:
            // The user has previously denied access
            setupResult = .notAuthorized
        }
    }
    
    // MARK: - UpdateUI
    
    private func updateUI() {
        switch recordState {
        case RecordState.loading:
            recordButton.setTitle("wait", for: .normal)
            recordButton.isEnabled = false
            recordLabel.text = "loading"
        case RecordState.ready:
            recordButton.setTitle("Start", for: .normal)
            recordButton.isEnabled = true
            recordLabel.text = ""
        case RecordState.recording:
            recordButton.setTitle("Stop", for: .normal)
            recordButton.isEnabled = true
            recordLabel.text = "recording..."
        case RecordState.saving:
            recordButton.setTitle("wait", for: .normal)
            recordButton.isEnabled = false
            recordLabel.text = "saving file..."
        }
    }
    
    // MARK: - Session Management

    // Call this on the session queue
    private func configureSession() {
        if setupResult.isSuccess == false {
            return
        }
        
        //ask for the tele device
        let videoDeviceDiscoverySession = AVCaptureDevice.DiscoverySession(deviceTypes: [cameraConfig.captureDevice], mediaType: .video, position: .back)

        let defaultRequiredDevice: AVCaptureDevice? = videoDeviceDiscoverySession.devices.first
        
        guard let videoDevice = defaultRequiredDevice else {
            setupResult = .configurationFailed(error: CameraError.noCaptureDevice)
            return
        }
        
        teleDevice = videoDevice
                
        do {
            videoDeviceInput = try AVCaptureDeviceInput(device: videoDevice)
        } catch {
            print("Could not create video device input: \(error)")
            setupResult = .configurationFailed(error: error)
            return
        }
        
        session.beginConfiguration()
        session.addInput(videoDeviceInput)
        session.sessionPreset = .hd4K3840x2160
        
        //ask for the microphone
        if let microphone = AVCaptureDevice.default(for: .audio), let audioInput = try? AVCaptureDeviceInput(device: microphone), session.canAddInput(audioInput) {
            print("added microphone")
            session.addInput(audioInput)
        }

        // Add a video data output
        if session.canAddOutput(videoDataOutput) {
            session.addOutput(videoDataOutput)
            videoDataOutput.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: Int(kCVPixelFormatType_32BGRA)]
            videoDataOutput.setSampleBufferDelegate(self, queue: dataOutputQueue)
        } else {
            setupResult = .configurationFailed(error: CameraError.cannotAddVideoOutput)
            session.commitConfiguration()
            return
        }
        
        if let connection = videoDataOutput.connection(with: .video) {
            //set orientation
            if connection.isVideoOrientationSupported {
                connection.videoOrientation = AVCaptureVideoOrientation.landscapeRight
            }
            //set intric matrix
            if connection.isCameraIntrinsicMatrixDeliverySupported {
                connection.isCameraIntrinsicMatrixDeliveryEnabled = true
            }
            
            if connection.isVideoStabilizationSupported {
                connection.preferredVideoStabilizationMode = .off
            }
        }

        session.commitConfiguration()

        session.startRunning()

        DispatchQueue.main.async {
            self.createVideoPreview()
        }
    }
    
    @IBAction func lockDevice() {
        var message = ""
        if let device = teleDevice {
            //lock focus
            if device.isLockingFocusWithCustomLensPositionSupported {
                do {
                    try device.lockForConfiguration()
                    //focus lens on infinity
                    device.setFocusModeLocked(lensPosition: 1.0, completionHandler: nil)
                    device.unlockForConfiguration()
                    cameraConfigButton.setTitle("✅ lock infinity", for: .normal)
                    message = message + "Focus:✅"
                }
                catch {
                    message = message + "Focus:\(error.localizedDescription)"
                }
            }
            
            //lock white balance
            if device.isWhiteBalanceModeSupported(.locked) {
                do {
                    try device.lockForConfiguration()
                    device.whiteBalanceMode = .locked
                    device.unlockForConfiguration()
                    cameraConfigButton.setTitle("✅ lock WB", for: .normal)
                    message = message + "WB:✅"
                }
                catch {
                    message = message + "WB:\(error.localizedDescription)"
                }
            }
            
            //lock exposure
            if device.isExposureModeSupported(.locked) {
                do {
                    try device.lockForConfiguration()
                    device.exposureMode = .locked
                    device.unlockForConfiguration()
                    cameraConfigButton.setTitle("✅ lock exposure", for: .normal)
                    message = message + "Exp:✅"
                }
                catch {
                    message = message + "WB:\(error.localizedDescription)"
                }
            }
        }
        cameraConfigButton.setTitle(message, for: .normal)
    }
    
    func createVideoPreview() {
        let previewLayer = AVCaptureVideoPreviewLayer(session: session )
        
        //set video orientation
        if let connection = previewLayer.connection {
            if connection.isVideoOrientationSupported {
                connection.videoOrientation = AVCaptureVideoOrientation.landscapeRight
            }
        }
        
        //set preview layer size
        previewLayer.bounds = videoView.bounds
        previewLayer.position = CGPoint(x: videoView.bounds.midX, y: videoView.bounds.midY)
        previewLayer.videoGravity = .resizeAspect
        
        videoView.layer.addSublayer(previewLayer)
        
        //set state to ready
        recordState = .ready
        updateUI()
    }
    
    func playClapSound() {
        if recordState == .recording {
            AudioServicesPlaySystemSound(1113)
            DispatchQueue.main.asyncAfter(deadline: .now() + 10.0) {
                self.playClapSound()
            }
        }
    }
    
    // MARK: - User Interaction

    @IBAction func recordButtonWasTouched() {
        switch recordState {
        case RecordState.ready:
            recordState = .recording
            startRecording()
        case RecordState.recording:
            recordState = .saving
            stopRecording()
        default:
            print("do nothing for now")
        }
        updateUI()
    }
    
    func startRecording() {
        //start recording
        startDate = Date()
        let metadata = Metadata.init(model: UIDevice.current.model, captureDevice: teleDevice.description, averageFPS:nil)
        videoMetadata = VideoMetadata.init(metadata: metadata, cameraCalibrationData: [CameraCalibration](), GNSSData: [GNSS](), IMUData: [IMU]())
        //if movieFileOutput wasn't connected to the session yet
        if movieFileOutput.connections.isEmpty {
            session.addOutput(movieFileOutput)
            
            //set orientation
            if let connection = movieFileOutput.connection(with: .video) {
                if connection.isVideoOrientationSupported {
                    connection.videoOrientation = AVCaptureVideoOrientation.landscapeRight
                }
            }
        }

        //set the right URL
        let fileManager = FileManager.default
        do {
            let name = UIDevice().name + "-" + startDate.description(with: Locale.current)
            let documentDirectory = try fileManager.url(for: .documentDirectory, in: .userDomainMask, appropriateFor:nil, create:true)
            videoOutputURL = documentDirectory.appendingPathComponent(name).appendingPathExtension("mov")
        }
        catch {
            print(error)
        }
        
        movieFileOutput.startRecording(to: videoOutputURL, recordingDelegate: self)
        
        //sound for video sync
        playClapSound()
    }
    
    func stopRecording() {
        //stop recording
        movieFileOutput.stopRecording()
    }
    
    // MARK: - AVCaptureFileOutputRecordingDelegate
    
    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo outputFileURL: URL, from connections: [AVCaptureConnection], error: Error?) {
        recordState = .ready
        updateUI()
        let activityViewController = UIActivityViewController(activityItems: [outputFileURL], applicationActivities: nil)
        self.present(activityViewController, animated: true, completion: nil)
    }

    func fileOutput(_ output: AVCaptureFileOutput, didStartRecordingTo fileURL: URL, from connections: [AVCaptureConnection]) {
        print("did start recording to \(fileURL)")
    }
    
    // MARK: - AVCaptureVideoDataOutputSampleBufferDelegate
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
                
        guard let exifMetadata = CMGetAttachment(sampleBuffer, key: "{Exif}" as CFString,  attachmentModeOut: nil) as? Dictionary<String, Any> else {return}

        if let cameraIntrinsicData = CMGetAttachment(sampleBuffer, key: kCMSampleBufferAttachmentKey_CameraIntrinsicMatrix, attachmentModeOut: nil) as? Data
        {
//            let matrix: matrix_float3x3 = cameraIntrinsicData.withUnsafeBytes { $0.pointee }
            var newCameraCalibration = CameraCalibration.init(exif: exifMetadata, cameraIntrinsicData: cameraIntrinsicData, cameraDistorsionMatrix: nil)
            if var cameraCalibrationData = videoMetadata?.cameraCalibrationData, var videoMetadata = videoMetadata  {
                cameraCalibrationData.append(newCameraCalibration)
                videoMetadata.cameraCalibrationData = cameraCalibrationData
            }
        }
    }
    
    func captureOutput(_ output: AVCaptureOutput, didDrop sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        print("did drop frame")
    }
}
