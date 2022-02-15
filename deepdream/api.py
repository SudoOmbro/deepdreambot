from time import sleep

from requests import post

from deepdream.utils import bytes_from_file


class ApiResult:

    def __init__(self, ok: bool, url: str = None, message: str = None):
        self.ok = ok
        self.url = url
        self.message = message


class DeepDreamAPI:

    _API_URL = "https://api.deepai.org/api/deepdream"
    _instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if DeepDreamAPI._instance is not None:
            raise Exception("This class is a singleton!")
        DeepDreamAPI._instance = self
        self._api_key: str = ""

    @staticmethod
    def get_instance():
        if DeepDreamAPI._instance is None:
            DeepDreamAPI._instance = DeepDreamAPI()
        return DeepDreamAPI._instance

    def set_api_key(self, api_key):
        self._api_key = api_key

    def dream(self, image: bytes or str) -> ApiResult:
        if not self._api_key:
            raise AttributeError("No API key was given!")
        if type(image) == bytes:
            r = post(
                url=self._API_URL,
                files={"image": image},
                headers={"api-key": self._api_key}
            )
        elif type(image) == str:
            r = post(
                url=self._API_URL,
                data={"image": image},
                headers={"api-key": self._api_key}
            )
        else:
            raise ValueError("Invalid image")
        if r.status_code == 200:
            result: dict = r.json()
            return ApiResult(
                ok=True,
                url=result["output_url"],
                message="Image processing ok"
            )
        return ApiResult(
            ok=False,
            message=r.json()
        )


if __name__ == '__main__':
    input_image: bytes or str = bytes_from_file("image.jpg")
    api = DeepDreamAPI.get_instance()
    api.set_api_key("c18c59d1-645a-4032-bc66-9ea79879c425")
    output: ApiResult or None = None
    for i in range(100):
        output = api.dream(input_image)
        if output.ok:
            print(f"iteration {i+1}: {output.url}")
            input_image = output.url
            sleep(2)
        else:
            break
    print(f"url: {output.url}, message: {output.message}")
