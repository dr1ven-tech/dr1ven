//
//  SeekerCell.swift
//  AVMetadataRecordPlay
//
//  Created by Matthieu Rouif on 11/12/2018.
//  Copyright © 2018 Apple. All rights reserved.
//

import UIKit

class SeekerCell: UICollectionViewCell {
	@IBOutlet weak var imageView: UIImageView!
	override init(frame: CGRect) {
		super.init(frame: frame)
	}
	
	required init?(coder aDecoder: NSCoder) {
		super.init(coder: aDecoder)
	}
}
