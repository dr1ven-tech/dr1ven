# Clones MaybeShewill-CV/lanenet-lane-detection

lanenet:
	@echo " *** Cloning lanenet-lane-detection"
	git clone https://github.com/MaybeShewill-CV/lanenet-lane-detection.git lanenet_tf
	@echo " *** Copying weights data"
	mkdir lanenet_tf/weights
	cp -R ~/data/lanenet/* lanenet_tf/weights
	@echo " *** Fixing imports :/"
	cd lanenet_tf && git grep -l 'from encoder_decoder_model' | xargs sed -i 's/from encoder_decoder_model/from perception.lane.lanenet.lanenet_tf.encoder_decoder_model/g'
	cd lanenet_tf && git grep -l 'from lanenet_model' | xargs sed -i 's/from lanenet_model/from perception.lane.lanenet.lanenet_tf.lanenet_model/g'

clean:
	rm -rf lanenet_tf
