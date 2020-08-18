import requests
from io import BytesIO
from PIL import Image
from tensorflow import keras

try:
    from PIL import ImageEnhance
    from PIL import Image as pil_image
except ImportError:
    pil_image = None
    ImageEnhance = None

if pil_image is not None:
    _PIL_INTERPOLATION_METHODS = {
        'nearest': pil_image.NEAREST,
        'bilinear': pil_image.BILINEAR,
        'bicubic': pil_image.BICUBIC,
    }
    # These methods were only introduced in version 3.4.0 (2016).
    if hasattr(pil_image, 'HAMMING'):
        _PIL_INTERPOLATION_METHODS['hamming'] = pil_image.HAMMING
    if hasattr(pil_image, 'BOX'):
        _PIL_INTERPOLATION_METHODS['box'] = pil_image.BOX
    # This method is new in version 1.1.3 (2013).
    if hasattr(pil_image, 'LANCZOS'):
        _PIL_INTERPOLATION_METHODS['lanczos'] = pil_image.LANCZOS


def get_image_from_url_and_convert_for_model(url, width_height_tuple=(299, 299), interpolation='nearest'):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resample = _PIL_INTERPOLATION_METHODS[interpolation]
    img = img.resize(width_height_tuple, resample)
    img = keras.preprocessing.image.img_to_array(img)
    img /= 255
    return img


def get_batches(dataset, batch_size):
    X = dataset
    n_samples = len(dataset)
    for start in range(0, n_samples, batch_size):
        end = min(start + batch_size, n_samples)
        yield X[start:end]
