/*
	Copyright (C) 2017 Apple Inc. All Rights Reserved.
	See LICENSE.txt for this sample’s licensing information
	
	Abstract:
	Player view controller
*/

import UIKit
import AVFoundation
import CoreMedia
import ImageIO
import MapKit

class PlayerViewController: UIViewController, AVPlayerItemMetadataOutputPushDelegate, UIDocumentPickerDelegate, MKMapViewDelegate {
	
	// MARK: View Controller Life Cycle
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		playButton.isEnabled = false
		pauseButton.isEnabled = false
		
		playerView.layer.backgroundColor = UIColor.black.cgColor
		
		let metadataQueue = DispatchQueue(label: "com.example.metadataqueue", attributes: [])
		itemMetadataOutput.setDelegate(self, queue: metadataQueue)
		
		self.annotatedMapView.delegate = self
	}
	
	override func viewDidDisappear(_ animated: Bool) {
		super.viewDidDisappear(animated)
		
		// Pause the player and start from the beginning if the view reappears.
		player?.pause()
		if playerAsset != nil {
			playButton.isEnabled = true
			pauseButton.isEnabled = false
			seekToZeroBeforePlay = false
			player?.seek(to: kCMTimeZero)
		}
	}
	
	override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
		super.viewWillTransition(to: size, with: coordinator)
		
		/*
			If device is rotated manually while playing back, and before the next orientation track is received,
			then playerLayer's frame should be changed to match with the playerView bounds.
		*/
		coordinator.animate(alongsideTransition: { _ in
				self.playerLayer?.frame = self.playerView.layer.bounds
			},
			completion: nil)
	}
	
	// MARK: Segue
	
	@IBAction func unwindBackToPlayer(segue: UIStoryboardSegue) {
		// Pull any data from the view controller which initiated the unwind segue.
		let assetGridViewController = segue.source as! AssetGridViewController
		if let selectedAsset = assetGridViewController.selectedAsset {
			if selectedAsset != playerAsset {
				setUpPlayback(for: selectedAsset)
				playerAsset = selectedAsset
			}
		}
	}
	
	
	@IBAction func didTapDocumentPicker() {
		let documentPicker = UIDocumentPickerViewController(documentTypes: ["com.apple.quicktime-movie"], in: .import)
		documentPicker.delegate = self
		self.present(documentPicker, animated: true, completion: nil)
	}

	// MARK: Player
	
	private var player: AVPlayer?
	
	private var seekToZeroBeforePlay = false
	
	private var playerAsset: AVAsset?
	
	@IBOutlet private weak var playerView: UIView!
	
	private var playerLayer: AVPlayerLayer?
	
	private var defaultVideoTransform = CGAffineTransform.identity
	
	private func setUpPlayback(for asset: AVAsset) {
		DispatchQueue.main.async {
			if let currentItem = self.player?.currentItem {
				currentItem.remove(self.itemMetadataOutput)
			}
			self.setUpPlayer(for: asset)
			self.playButton.isEnabled = true
			self.pauseButton.isEnabled = false
			self.removeAllSublayers(from: self.facesLayer)
			self.annotatedMapView.removeOverlays(self.annotatedMapView.overlays)
			self.annotatedMapView.removeAnnotations(self.annotatedMapView.annotations)

			self.readMetadataFromAsset(asset: asset, handler: { (result) in
				switch result {
					case .Success:
					self.drawPathOnMap()
					case .Failure(let error):
						print("Could not get location metadata track from asset: \(String(describing: error)))")
				}
			})
		}
	}
	
	@IBOutlet private weak var annotatedMapView: AnnotatedMapView!
	
	private var reader: AVAssetReader?
	
	private var readerMetadataOutput: AVAssetReaderTrackOutput?
	
	private var metadataAdaptor: AVAssetReaderOutputMetadataAdaptor?

	private var readerQueue = DispatchQueue(label: "com.example.readerqueue", attributes: [])
	
	private var currentPin = MKPointAnnotation()
	
	private var timeStamps = [NSValue]()
	
	private var locationPoints = [CLLocation]()
	
	private var shouldCenterMapView = true

	@IBOutlet private weak var locationOverlayLabel: UILabel!

	private func setUpPlayer(for asset: AVAsset) {
		let mutableComposition = AVMutableComposition()
		
		// Create a mutableComposition for all the tracks present in the asset.
		guard let sourceVideoTrack = asset.tracks(withMediaType: AVMediaTypeVideo).first else {
			print("Could not get video track from asset")
			return
		}
		defaultVideoTransform = sourceVideoTrack.preferredTransform
		
		let sourceAudioTrack = asset.tracks(withMediaType: AVMediaTypeAudio).first
		let mutableCompositionVideoTrack = mutableComposition.addMutableTrack(withMediaType: AVMediaTypeVideo, preferredTrackID: kCMPersistentTrackID_Invalid)
		let mutableCompositionAudioTrack = mutableComposition.addMutableTrack(withMediaType: AVMediaTypeAudio, preferredTrackID: kCMPersistentTrackID_Invalid)
		
		do {
			try mutableCompositionVideoTrack.insertTimeRange(CMTimeRangeMake(kCMTimeZero, asset.duration), of: sourceVideoTrack, at: kCMTimeZero)
			if let sourceAudioTrack = sourceAudioTrack {
				try mutableCompositionAudioTrack.insertTimeRange(CMTimeRangeMake(kCMTimeZero, asset.duration), of: sourceAudioTrack, at: kCMTimeZero)
			}
		}
		catch {
			print("Could not insert time range into video/audio mutable composition: \(error)")
		}
		
		for metadataTrack in asset.tracks(withMediaType: AVMediaTypeMetadata) {
			if track(metadataTrack, hasMetadataIdentifier:AVMetadataIdentifierQuickTimeMetadataDetectedFace) ||
				track(metadataTrack, hasMetadataIdentifier:AVMetadataIdentifierQuickTimeMetadataVideoOrientation) ||
				track(metadataTrack, hasMetadataIdentifier:AVMetadataIdentifierQuickTimeMetadataLocationISO6709) {
				
				let mutableCompositionMetadataTrack = mutableComposition.addMutableTrack(withMediaType: AVMediaTypeMetadata, preferredTrackID: kCMPersistentTrackID_Invalid)
				
				do {
					try mutableCompositionMetadataTrack.insertTimeRange(CMTimeRangeMake(kCMTimeZero, asset.duration), of: metadataTrack, at: kCMTimeZero)
				}
				catch let error as NSError {
					print("Could not insert time range into metadata mutable composition: \(error)")
				}
			}
		}
		
		// Get an instance of AVPlayerItem for the generated mutableComposition.
		// let playerItem = AVPlayerItem(asset: asset) // This doesn't support video orientation hence we use a mutable composition.
		let playerItem = AVPlayerItem(asset: mutableComposition)
		playerItem.add(itemMetadataOutput)

		if let player = player {
			player.replaceCurrentItem(with: playerItem)
		}
		else {
			// Create AVPlayer with the generated instance of playerItem. Also add the facesLayer as subLayer to this playLayer.
			player = AVPlayer(playerItem: playerItem)
			player?.actionAtItemEnd = .none
			
			let playerLayer = AVPlayerLayer(player: player)
			playerLayer.backgroundColor = UIColor.darkGray.cgColor
			playerLayer.addSublayer(facesLayer)
			playerView.layer.addSublayer(playerLayer)
			facesLayer.frame = playerLayer.videoRect;
			
			self.playerLayer = playerLayer
		}
		
		// Update the player layer to match the video's default transform. Disable animation so the transform applies immediately.
		CATransaction.begin()
		CATransaction.setDisableActions(true)
		playerLayer?.transform = CATransform3DMakeAffineTransform(defaultVideoTransform)
		playerLayer?.frame = playerView.layer.bounds
		CATransaction.commit()
		
		// When the player item has played to its end time we'll toggle the movie controller Pause button to be the Play button.
		NotificationCenter.default.addObserver(self, selector: #selector(playerItemDidReachEnd(_:)), name: NSNotification.Name.AVPlayerItemDidPlayToEndTime, object: player?.currentItem)
		
		seekToZeroBeforePlay = false
	}
	
	/// Called when the player item has played to its end time.
	func playerItemDidReachEnd(_ notification: Notification) {
		// After the movie has played to its end time, seek back to time zero to play it again.
		seekToZeroBeforePlay = true
		playButton.isEnabled = true
		pauseButton.isEnabled = false
		removeAllSublayers(from: facesLayer)
	}
	
	@IBOutlet private weak var playButton: PlayerButton!
	
	@IBAction private func playButtonTapped(_ sender: AnyObject) {
		if seekToZeroBeforePlay {
			seekToZeroBeforePlay = false
			player?.seek(to: kCMTimeZero)
			
			// Update the player layer to match the video's default transform.
			playerLayer?.transform = CATransform3DMakeAffineTransform(defaultVideoTransform)
			playerLayer?.frame = playerView.layer.bounds
		}
		
		player?.play()
		playButton.isEnabled = false
		pauseButton.isEnabled = true
	}
	
	@IBOutlet private weak var pauseButton: PlayerButton!
	
	@IBAction private func pauseButtonTapped(_ sender: AnyObject) {
		player?.pause()
		playButton.isEnabled = true
		pauseButton.isEnabled = false
	}
	
	// MARK: Timed Metadata
	
	private let itemMetadataOutput = AVPlayerItemMetadataOutput(identifiers: nil)
	
	private var honorTimedMetadataTracksDuringPlayback = true
	
	func metadataOutput(_ output: AVPlayerItemMetadataOutput, didOutputTimedMetadataGroups groups: [AVTimedMetadataGroup], from track: AVPlayerItemTrack) {
		for metadataGroup in groups {
			
			DispatchQueue.main.async {
				
				// Sometimes the face/location track wouldn't contain any items because of scene change, we should remove previously drawn faceRects/locationOverlay in that case.
				if metadataGroup.items.count == 0 {
					if self.track(track.assetTrack, hasMetadataIdentifier: AVMetadataIdentifierQuickTimeMetadataDetectedFace) {
						self.removeAllSublayers(from: self.facesLayer)
					}
					else if self.track(track.assetTrack, hasMetadataIdentifier: AVMetadataIdentifierQuickTimeMetadataVideoOrientation) {
						self.locationOverlayLabel.text = ""
					}
				}
				else {
					var faces = [AVMetadataObject]()
					
					for metdataItem in metadataGroup.items {
						guard let itemIdentifier = metdataItem.identifier, let itemDataType = metdataItem.dataType else {
							continue
						}
						
						switch itemIdentifier {
							case AVMetadataIdentifierQuickTimeMetadataDetectedFace:
								if let itemValue = metdataItem.value as? AVMetadataObject {
									faces.append(itemValue)
								}
							
							case AVMetadataIdentifierQuickTimeMetadataVideoOrientation:
								if itemDataType == String(kCMMetadataBaseDataType_SInt16) {
									if let videoOrientationValue = metdataItem.value as? NSNumber {
										let sourceVideoTrack = self.playerAsset!.tracks(withMediaType: AVMediaTypeVideo)[0]
										let videoDimensions = CMVideoFormatDescriptionGetDimensions(sourceVideoTrack.formatDescriptions[0] as! CMVideoFormatDescription)
										if let videoOrientation = CGImagePropertyOrientation(rawValue: videoOrientationValue.uint32Value) {
											let orientationTransform = self.affineTransform(for:videoOrientation, with:videoDimensions)
											let rotationTransform = CATransform3DMakeAffineTransform(orientationTransform)
											
											// Remove faceBoxes before applying transform and then re-draw them as we get new face coordinates.
											self.removeAllSublayers(from: self.facesLayer)
											self.playerLayer?.transform = rotationTransform
											self.playerLayer?.frame = self.playerView.layer.bounds
										}
									}
								}
							
							case AVMetadataIdentifierQuickTimeMetadataLocationISO6709:
								
								if itemDataType == String(kCMMetadataDataType_QuickTimeMetadataLocation_ISO6709) {
									if let itemValue = metdataItem.value as? String {
										self.locationOverlayLabel.text = itemValue
										if let location = self.locationFromLocationMetadataItem(metdataItem: metdataItem) {
											self.updateCurrentLocation(location: location)
										}
									}
								}
							
							default:
								print("Timed metadata: unrecognized metadata identifier \(itemIdentifier)")
						}
					}
					
					if faces.count > 0 {
						self.drawFaceMetadataRects(faces)
					}
				}
			}
		}
	}
	
	private func track(_ track: AVAssetTrack, hasMetadataIdentifier metadataIdentifier: String) -> Bool {
		let formatDescription = track.formatDescriptions[0] as! CMFormatDescription
		if let metadataIdentifiers = CMMetadataFormatDescriptionGetIdentifiers(formatDescription) as NSArray? {
			if metadataIdentifiers.contains(metadataIdentifier) {
				return true
			}
		}
		
		return false
	}
	
	private let facesLayer = CALayer()
	
	private func drawFaceMetadataRects(_ faces: [AVMetadataObject]) {
		guard let playerLayer = playerLayer else { return }
		
		DispatchQueue.main.async {
			
			let viewRect = playerLayer.videoRect
			self.facesLayer.frame = viewRect
			self.facesLayer.masksToBounds = true
			self.removeAllSublayers(from: self.facesLayer)
			
			for face in faces {
				let faceBox = CALayer()
				let faceRect = face.bounds
				let viewFaceOrigin = CGPoint(x: faceRect.origin.x * viewRect.size.width, y: faceRect.origin.y * viewRect.size.height)
				let viewFaceSize = CGSize(width: faceRect.size.width * viewRect.size.width, height: faceRect.size.height * viewRect.size.height)
				let viewFaceBounds = CGRect(x: viewFaceOrigin.x, y: viewFaceOrigin.y, width: viewFaceSize.width, height: viewFaceSize.height)
				
				CATransaction.begin()
				CATransaction.setDisableActions(true)
				self.facesLayer.addSublayer(faceBox)
				faceBox.masksToBounds = true
				faceBox.borderWidth = 1.0
				faceBox.borderColor = UIColor(red: CGFloat(0.3), green: CGFloat(0.6), blue: CGFloat(0.9), alpha: CGFloat(0.7)).cgColor
				faceBox.cornerRadius = 2.0
				faceBox.frame = viewFaceBounds
				CATransaction.commit()
				
				PlayerViewController.updateAnimation(for: self.facesLayer, removeAnimation: true)
			}
		}
	}
	
	// MARK: Asset reading
	
	enum Result: Equatable{
		case Success
		case Failure(Error?)
		
		static func == (lhs: Result, rhs: Result) -> Bool {
			switch (lhs, rhs) {
			case (.Success, .Success):
				return true
			default:
				return false
			}
		}
	}

	typealias Handler = (Result) -> Void
	
	func readMetadataFromAsset(asset: AVAsset, handler: @escaping Handler) {
		asset.loadValuesAsynchronously(forKeys: ["tracks"]) {
			// Dispatch all the reading work to a background queue, so we do not block the main thread
			self.readerQueue.async {
				var result: Result
				var error: NSError?
				
				// Set up the AVAssetReader reading samples or flag an error
				if (asset.statusOfValue(forKey: "tracks", error: &error) == AVKeyValueStatus.loaded) {
					result = self.setupReaderForAsset(asset: asset)
				}
				else {
					result = Result.Failure(error)
				}

//				 Start reading in the location metadata from asset reader output, which we can later draw on a map
				if (result == Result.Success) {
					result = self.startReadingLocationMetadata()
				}
				
				if (result == Result.Success) {
					if (self.locationPoints.count > 0) {
						result = Result.Success
					}
					else {
						result = Result.Failure(nil)
					}
				}
				else {
					self.reader?.cancelReading()
				}

				DispatchQueue.main.async {
					handler(result)
				}
			}
		}
	}
	
	func setupReaderForAsset(asset: AVAsset) -> Result {
		var locationTrack: AVAssetTrack?
		do {
			self.reader = try AVAssetReader(asset: asset)
			for metadataTrack in asset.tracks(withMediaType: AVMediaTypeMetadata) {
				if track(metadataTrack, hasMetadataIdentifier:AVMetadataIdentifierQuickTimeMetadataLocationISO6709) {
					locationTrack = metadataTrack
				}
			}
			
			if let locationTrack = locationTrack {
				self.readerMetadataOutput = AVAssetReaderTrackOutput(track: locationTrack, outputSettings: nil)
				if let readerMetadataOutput = self.readerMetadataOutput {
					self.metadataAdaptor = AVAssetReaderOutputMetadataAdaptor(assetReaderTrackOutput: readerMetadataOutput)
					reader?.add(readerMetadataOutput)
					return Result.Success
				}
			}
			return Result.Failure(nil)
		}
		catch let error {
			return Result.Failure(error)
		}
	}
	
	func startReadingLocationMetadata() -> Result {
		// Instruct the asset reader to get ready to do work
		if let _ = self.reader?.startReading() {
			// Read in all the timed metadata groups from the track and save it in an array to use for drawing on the map later
			// The corresponding time stamps for the location data are stored in another array
			if let metadataAdaptor = self.metadataAdaptor {
				locationPoints.removeAll()
				while let group = metadataAdaptor.nextTimedMetadataGroup() {
					if let location = self.locationFromMetadataGroup(metadataGroup: group) {
						locationPoints.append(location)
						timeStamps.append(NSValue(timeRange: group.timeRange))
					}
				}
				return Result.Success
			}
		}
		return Result.Failure(nil)
	}
	
	// MARK: Utilities
	
	func drawPathOnMap() {
		let pointsToUse = locationPoints.map { $0.coordinate }
		
		// Draw the extracted path as an overlay on the map view
		let polyline = MKPolyline(coordinates: pointsToUse, count: pointsToUse.count)
		self.annotatedMapView.add(polyline, level: .aboveRoads)
		
		// Set initial coordinate to the starting coordinate of the path
		if let firstCoordinate = locationPoints.first {
			self.annotatedMapView.centerCoordinate = firstCoordinate.coordinate
		}
		
		// Set initial region to some region around the starting coordinate
		if let firstPoint = locationPoints.first, let lastPoint = locationPoints.last {
			let longitudeDelta = 2.2 * abs(_:firstPoint.coordinate.longitude - lastPoint.coordinate.longitude)
			let latitudeDelta = 2.2 * abs(_:firstPoint.coordinate.latitude - lastPoint.coordinate.latitude)
			self.annotatedMapView.region = MKCoordinateRegionMake(self.annotatedMapView.centerCoordinate, MKCoordinateSpanMake(latitudeDelta, longitudeDelta))
		}
		else {
			self.annotatedMapView.region = MKCoordinateRegionMakeWithDistance(self.annotatedMapView.centerCoordinate, 800, 800)
		}
//
		

		self.currentPin.coordinate = self.annotatedMapView.centerCoordinate
		self.annotatedMapView.addAnnotation(self.currentPin)
	}
	
	func locationFromMetadataGroup(metadataGroup: AVTimedMetadataGroup) -> CLLocation? {
		// Go through the timed metadata group to extract location value
		for item in metadataGroup.items
		{
			if let location = locationFromLocationMetadataItem(metdataItem: item) {
				return location
			}
		}
		
		return nil;
	}
	
	func locationFromLocationMetadataItem(metdataItem: AVMetadataItem) -> CLLocation? {
		
		guard let _ = metdataItem.identifier, let itemDataType = metdataItem.dataType else {
			return nil
		}

		// Go through the timed metadata group to extract location value
		if itemDataType == String(kCMMetadataDataType_QuickTimeMetadataLocation_ISO6709) {
			if let itemValue = metdataItem.value as? String {
				
				// Extract from a string in iso6709 notation
				let latitudeRange =  itemValue.startIndex..<itemValue.index(itemValue.startIndex, offsetBy: 8)
				let latitude = itemValue[latitudeRange]

				let longitudeRange = itemValue.index(itemValue.startIndex, offsetBy: 8)..<itemValue.index(itemValue.startIndex, offsetBy: 17)
				let longitude = itemValue[longitudeRange]
				
				guard let longitudeValue = Double(longitude), let latitudeValue = Double(latitude) else {
					return nil
				}
				
				let location = CLLocation(latitude: latitudeValue, longitude: longitudeValue)
				return location
			}
		}
		return nil
	}
	
	func updateCurrentLocation(location: CLLocation)
	{
		// Update current pin to the new location
		DispatchQueue.main.async {
			self.currentPin.coordinate = location.coordinate
			self.annotatedMapView.setCenter(location.coordinate, animated: true)
			self.annotatedMapView.addAnnotation(self.currentPin)
		}
	}
	
	// MARK: Animation Utilities
	
	class private func updateAnimation(for layer: CALayer, removeAnimation remove: Bool) {
		if remove {
			layer.removeAnimation(forKey: "animateOpacity")
		}
		
		if layer.animation(forKey: "animateOpacity") == nil {
			layer.isHidden = false
			let opacityAnimation = CABasicAnimation(keyPath: "opacity")
			opacityAnimation.duration = 0.3
			opacityAnimation.repeatCount = 1.0
			opacityAnimation.autoreverses = true
			opacityAnimation.fromValue = 1.0
			opacityAnimation.toValue = 0.0
			layer.add(opacityAnimation, forKey: "animateOpacity")
		}
	}
	
	private func removeAllSublayers(from layer: CALayer) {
		CATransaction.begin()
		CATransaction.setDisableActions(true)
		
		if let sublayers = layer.sublayers {
			for layer in sublayers {
				layer.removeFromSuperlayer()
			}
		}
		
		CATransaction.commit()
	}
	
	private func affineTransform(for videoOrientation: CGImagePropertyOrientation, with videoDimensions: CMVideoDimensions) -> CGAffineTransform {
		var transform = CGAffineTransform.identity
		
		// Determine rotation and mirroring from tag value.
		var rotationDegrees = 0
		var mirror = false
		
		switch videoOrientation {
			case .up:				rotationDegrees = 0;	mirror = false
			case .upMirrored:		rotationDegrees = 0;	mirror = true
			case .down:				rotationDegrees = 180;	mirror = false
			case .downMirrored:		rotationDegrees = 180;	mirror = true
			case .left:				rotationDegrees = 270;	mirror = false
			case .leftMirrored:		rotationDegrees = 90;	mirror = true
			case .right:			rotationDegrees = 90;	mirror = false
			case .rightMirrored:	rotationDegrees = 270;	mirror = true
		}
		
		// Build the affine transform.
		var angle: CGFloat = 0.0 // in radians
		var tx: CGFloat = 0.0
		var ty: CGFloat = 0.0
		
		switch rotationDegrees {
			case 90:
				angle = CGFloat(Double.pi / 2.0)
				tx = CGFloat(videoDimensions.height)
				ty = 0.0
				
			case 180:
				angle = CGFloat(Double.pi)
				tx = CGFloat(videoDimensions.width)
				ty = CGFloat(videoDimensions.height)
				
			case 270:
				angle = CGFloat(Double.pi / -2.0)
				tx = 0.0
				ty = CGFloat(videoDimensions.width)
				
			default:
				break
		}
		
		// Rotate first, then translate to bring 0,0 to top left.
		if angle == 0.0 {	// and in this case, tx and ty will be 0.0
			transform = CGAffineTransform.identity
		}
		else {
			transform = CGAffineTransform(rotationAngle: angle)
			transform = transform.concatenating(CGAffineTransform(translationX: tx, y: ty))
		}
		
		// If mirroring, flip along the proper axis.
		if mirror {
			transform = transform.concatenating(CGAffineTransform(scaleX: -1.0, y: 1.0))
			transform = transform.concatenating(CGAffineTransform(translationX: CGFloat(videoDimensions.height), y: 0.0))
		}
		
		return transform
	}
	
	
	// MARK: UIDocumentPickerDelegate
	
	func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentAt url: URL) {
		let selectedAsset = AVAsset(url: url)
		if selectedAsset != playerAsset {
			setUpPlayback(for: selectedAsset)
			playerAsset = selectedAsset
		}
	}
	
	// MARK: MapViewDelegate
	
	func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
		let polylineRenderer = MKPolylineRenderer(overlay: overlay)
		polylineRenderer.lineWidth = 5.0
		polylineRenderer.strokeColor =  UIColor(red: 0.1, green: 0.5, blue: 0.98, alpha: 0.8)
		return polylineRenderer
	}
}
