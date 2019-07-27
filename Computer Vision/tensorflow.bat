Set PYTHONPATH=%PYTHONPATH%;C:/User/AppData/Local/Continuum/Anaconda3/Lib/site-packages/tensorflow/models/
Set PYTHONPATH=%PYTHONPATH%;C:/UserAppData/Local/Continuum/Anaconda3/Lib/site-packages/tensorflow/models/slim

start "TF Train" cmd /k ^
C:\User\AppData\Local\Continuum\Anaconda3\python ^
C:\User\AppData\Local\Continuum\Anaconda3\Lib\site-packages\tensorflow\models\object_detection\train.py ^
--logtostderr ^
--pipeline_config_path=C:\User\Documents\project\ssd_mobilenet_v1_data.config ^
--train_dir=C:\User\Documents\project\train

start "TF Evaluate" cmd /k ^
C:\User\AppData\Local\Continuum\Anaconda3\python ^
C:\User\AppData\Local\Continuum\Anaconda3\Lib\site-packages\tensorflow\models\object_detection\eval.py ^
--logtostderr ^
--pipeline_config_path=C:\User\project\ssd_mobilenet_v1_data.config ^
--checkpoint_dir=C:\User\project\checkpoints ^
--eval_dir=C:\User\project\test

start "Tensorboard" cmd /k ^
C:\User\AppData\Local\Continuum\Anaconda3\Scripts\tensorboard ^
--logdir=C:\User\project\train ^
--host=localhost

REM Tensorboard @ http://127.0.0.1:6006
