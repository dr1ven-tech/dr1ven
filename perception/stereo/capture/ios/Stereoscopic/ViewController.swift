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

class ViewController: UIViewController, AVCaptureFileOutputRecordingDelegate, AVCaptureVideoDataOutputSampleBufferDelegate {

    @IBOutlet weak var videoView: UIView!
    
    private enum SessionSetupResult {
        case success
        case notAuthorized
        case configurationFailed
    }
    
    private enum RecordState {
        case loading
        case ready
        case recording
        case saving
    }

    
    private var setupResult: SessionSetupResult = .success
    private let session = AVCaptureSession()
    private var isSessionRunning = false
    private var recordState: RecordState = .loading
    private var teleDevice: AVCaptureDevice!
    private var videoDeviceInput: AVCaptureDeviceInput!
    private var statusBarOrientation: UIInterfaceOrientation = .landscapeRight
    private var outputURL: URL!
    
    private var startDate: Date!
    private var movieFileOutput = AVCaptureMovieFileOutput()
    // Communicate with the session and other session objects on this queue.
    private let sessionQueue = DispatchQueue(label: "session queue", attributes: [], autoreleaseFrequency: .workItem)
    
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
        if setupResult != .success {
            return
        }
        
        //ask for the tele device
        let videoDeviceDiscoverySession = AVCaptureDevice.DiscoverySession(deviceTypes: [.builtInTelephotoCamera], mediaType: .video, position: .back)

        let defaultTeleDevice: AVCaptureDevice? = videoDeviceDiscoverySession.devices.first
        
        guard let videoDevice = defaultTeleDevice else {
            print("Could not find any video device")
            setupResult = .configurationFailed
            return
        }
        
        teleDevice = defaultTeleDevice
                
        do {
            videoDeviceInput = try AVCaptureDeviceInput(device: videoDevice)
        } catch {
            print("Could not create video device input: \(error)")
            setupResult = .configurationFailed
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
            print("Could not add video data output to the session")
            setupResult = .configurationFailed
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
                print("intrinsic matrix enabled")
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
            outputURL = documentDirectory.appendingPathComponent(name).appendingPathExtension("mov")
        }
        catch {
            print(error)
        }
        
        movieFileOutput.startRecording(to: outputURL, recordingDelegate: self)
        
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
        if let cameraIntrinsicData = CMGetAttachment(sampleBuffer, key: kCMSampleBufferAttachmentKey_CameraIntrinsicMatrix, attachmentModeOut: nil) as? Data
        {
            let matrix: matrix_float3x3 = cameraIntrinsicData.withUnsafeBytes { $0.pointee }
            print(matrix)
        }
    }
    
    func captureOutput(_ output: AVCaptureOutput, didDrop sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        print("did drop frame")
    }

}
