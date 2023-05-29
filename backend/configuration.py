import os

PORT = 7070
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH_TO_WORDS = PROJECT_ROOT + '\\dataset\\words\\'
PATH_TO_IMAGES = PATH_TO_WORDS + 'iam_words\\words\\'
PATH_TO_FORMS = PROJECT_ROOT + '\\dataset\\sentences\\metadata\\forms.txt'
PATH_TO_SENTENCES_IMAGES = PROJECT_ROOT + '\\dataset\\sentences\\dataset\\'
PATH_TO_SAVED_FOLDER = PROJECT_ROOT + '\\saved\\'
TRAIN_SIZE = 0.8
VALIDATION_SIZE = 0.54
BATCH_SIZE = 64
PADDING_TOKEN = 99
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 32

