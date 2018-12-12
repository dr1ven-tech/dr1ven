//
//  SeekerViewDatasource.swift
//  AVMetadataRecordPlay
//
//  Created by Matthieu Rouif on 11/12/2018.
//  Copyright © 2018 Apple. All rights reserved.
//

import UIKit
import AVFoundation

let secondsPerFrame: Int32 = 3

struct SeekerThumbnail {
	let image: UIImage
	let time: CMTime
}

class SeekerViewDataSource: NSObject, UICollectionViewDataSource {
	var thumbnails = [SeekerThumbnail]()
	var thumbTimes = [CMTime]()
	var collectionView: UICollectionView
	var asset: AVAsset {
		didSet{
			//reload datasource
			self.generateThumbnails(asset: asset)
		}
	}
	
	init(asset: AVAsset, collectionView: UICollectionView) {
		self.asset = asset
		self.collectionView = collectionView
		super.init()
		self.generateThumbnails(asset: asset)
	}
	
	func generateThumbnails(asset: AVAsset) {
		let duration = Float(asset.duration.value) / Float(asset.duration.timescale)
		let numberOfEntireFrames = Int(ceil(duration/Float(secondsPerFrame)))
		//let contentWidth = Float(duration.value)/Float(duration.timescale)/timePerPixel
		//let contentHeight = Float(self.frame.height)
		//
		var thumbTimesAsValues = [NSValue]()
		for i in 0...numberOfEntireFrames {
			let timeValue = CMTimeValue(secondsPerFrame * asset.duration.timescale * Int32(i))
			let time = CMTime(value: timeValue, timescale: asset.duration.timescale)
			let value = NSValue(time: time)
			thumbTimes.append(time)
			thumbTimesAsValues.append(value)
		}
		//
		let assetGenerator = AVAssetImageGenerator(asset: asset)
		assetGenerator.generateCGImagesAsynchronously(forTimes: thumbTimesAsValues) { (completionRequestedTime, image, actualTime, result, error) in
			switch result {
			case .succeeded:
				if let image = image {
					let uiimage = UIImage(cgImage: image)
					let seekerThumbnail = SeekerThumbnail(image: uiimage, time: actualTime)
					self.thumbnails.append(seekerThumbnail)
					
					//sort
					self.thumbnails = self.thumbnails.sorted(by: { (seekerThum1, seekerThumb2) -> Bool in
						return seekerThum1.time.value < seekerThumb2.time.value
					})
					let index = self.indexForTime(targetTime: actualTime)
					DispatchQueue.main.async {
						self.collectionView.reloadItems(at: [IndexPath(row: index, section: 0)])
					}
				}
			case .failed:
				print("thumbnail failed")
			case .cancelled:
				print("thumbnail cancelled")
			}
		}
	}
	
	func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
		let duration = Float(asset.duration.value) / Float(asset.duration.timescale)
		let numberOfEntireFrames = Int(ceil(duration/Float(secondsPerFrame)))
		return numberOfEntireFrames
	}
	
	func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
		let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "thumbnailIdentifier", for: indexPath) as! SeekerCell
		let time = timeForIndex(index: indexPath.row)
		if let seekerThumb = self.closestSeekerThumb(time: time) {
			cell.imageView.image = seekerThumb.image
		}
		else {
//			placeholder
			cell.imageView.image = nil
		}
		return cell
	}
	
	func timeForIndex(index: Int) -> CMTime {
		return thumbTimes[index]
	}
	
	func indexForTime(targetTime: CMTime) -> Int {
		guard self.thumbTimes.count > 0 else { return 0 }
		var minIndex = 0
		var minDistance = kCMTimeMaxTimescale
		for (index, time) in self.thumbTimes.enumerated() {
			let distance = abs(targetTime.value - time.value)
			if distance < minDistance {
				minIndex = index
				minDistance = Int(distance)
			}
		}
		return minIndex
	}
	
	func closestSeekerThumb(time: CMTime) -> SeekerThumbnail? {
		guard self.thumbnails.count > 0 else { return nil }
		var minIndex = 0
		var minDistance = kCMTimeMaxTimescale
		for (index, seekerThumbnail) in self.thumbnails.enumerated() {
			let distance = abs(seekerThumbnail.time.value - time.value)
			if distance < minDistance {
				minIndex = index
				minDistance = Int(distance)
			}
		}
		return self.thumbnails[minIndex]
	}
}
