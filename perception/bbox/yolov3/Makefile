# Clones and build Darknet

darknet:
	@echo " *** Cloning darknet"
	git clone https://github.com/pjreddie/darknet
	@echo " *** Making darknet"
	cd darknet/ && make
	@echo " *** Downloading YOLOv3 weights"
	cd darknet/ && wget https://pjreddie.com/media/files/yolov3.weights
	@echo " *** Patching the python module"
	cp mod/darknet.py darknet/python/

clean:
	rm -rf darknet
