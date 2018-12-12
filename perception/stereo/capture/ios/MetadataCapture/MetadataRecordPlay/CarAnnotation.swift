//
//  CarAnnotation.swift
//  AVMetadataRecordPlay
//
//  Created by Matthieu Rouif on 12/12/2018.
//  Copyright © 2018 Apple. All rights reserved.
//

import UIKit
import MapKit

class CarAnnotation: MKAnnotationView {
	override init(annotation: MKAnnotation?, reuseIdentifier: String?) {
		super.init(annotation: annotation, reuseIdentifier: reuseIdentifier)
		self.image = UIImage(named: "map_car")
	}
	
	required init?(coder aDecoder: NSCoder) {
		fatalError("init(coder:) has not been implemented")
	}
}
