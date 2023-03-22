import os
import urllib
import time
import requests
import regex

BING_URL = "https://www.bing.com"


class ImageGen:
    """
    Image generation by Microsoft Bing
    Parameters:
        auth_cookie: str
    """

    def __init__(self, auth_cookie: str) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "referrer": "https://www.bing.com/images/create/",
            "origin": "https://www.bing.com",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63",
        }
        self.session.cookies.set("_U", auth_cookie)

    def getImages(self, prompt: str) -> list:
        """
        Fetches image links from Bing
        Parameters:
            prompt: str
        """
        url_encoded_prompt = urllib.parse.quote(prompt)
        # https://www.bing.com/images/create?q=<PROMPT>&rt=4&FORM=GENCRE
        url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=4&FORM=GENCRE"
        response = self.session.post(url, allow_redirects=False)
        # Get redirect URL
        redirect_url = response.headers["Location"]
        print(redirect_url)
        request_id = redirect_url.split("id=")[-1]
        self.session.get(f"{BING_URL}{redirect_url}")
        # https://www.bing.com/images/create/async/results/{ID}?q={PROMPT}
        polling_url = f"{BING_URL}/images/create/async/results/{request_id}?q={url_encoded_prompt}"
        # Poll for results
        while True:
            response = self.session.get(polling_url)
            if response.text == "":
                time.sleep(1)
                continue
            else:
                break

        # Use regex to search for src=""
        image_links = regex.findall(r'src="([^"]+)"', response.text)
        # Remove duplicates
        return list(set(image_links))

    def saveImages(self, links: list, output_dir: str) -> None:
        """
        Saves images to output directory
        """
        os.mkdir(args.output_dir)
        image_num = 0
        for link in links:
            with self.session.get(link, stream=True) as response:
                # save response to file
                response.raise_for_status()
                with open(
                    f"{output_dir}/{image_num}.jpeg", "wb", encoding="utf-8"
                ) as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

            image_num += 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--U", help="Auth cookie from browser", type=str, required=True)
    parser.add_argument(
        "--prompt", help="Prompt to generate images for", type=str, required=True
    )
    parser.add_argument(
        "--output-dir", help="Output directory", type=str, default="./output"
    )
    args = parser.parse_args()
    # Create image generator
    image_generator = ImageGen(args.U)
    image_generator.saveImages(
        image_generator.getImages(args.prompt), output_dir=args.output_dir
    )