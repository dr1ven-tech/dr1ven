//
//  File.swift
//  AVMetadataRecordPlay
//
//  Created by Matthieu Rouif on 11/12/2018.
//  Copyright © 2018 Apple. All rights reserved.
//
import UIKit
import AVFoundation

class SeekerView: UICollectionView {
	init(frame: CGRect) {
		let layout = UICollectionViewFlowLayout()
		layout.itemSize = CGSize(width: frame.height, height: frame.height)
		layout.minimumInteritemSpacing = 0
		layout.minimumLineSpacing = 0
		layout.scrollDirection = .horizontal
		super.init(frame: frame, collectionViewLayout: layout)
	}
	
	required init?(coder aDecoder: NSCoder) {
		super.init(coder: aDecoder)
	}
}

class SeekerViewFlowLayout: UICollectionViewFlowLayout {
	init(frame: CGRect) {
		super.init()
		self.itemSize = CGSize(width: frame.height, height: frame.height)

		self.minimumInteritemSpacing = 0
		self.minimumLineSpacing = 0.5
		self.scrollDirection = .horizontal
		self.sectionInset = UIEdgeInsetsMake(0, frame.width/2, 0, frame.width/2)
	}
	
	required init?(coder aDecoder: NSCoder) {
		fatalError("init(coder:) has not been implemented")
	}
}
