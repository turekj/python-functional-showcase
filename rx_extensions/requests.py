import requests
import rx


def rx_request(method, url, **kwargs):
    def subscribe(observer):
        response = requests.request(method, url, **kwargs)

        try:
            response.raise_for_status()
            observer.on_next(response)
            observer.on_completed()
        except requests.HTTPError as e:
            observer.on_error(e)

        return lambda: None

    return rx.Observable.create(subscribe)


def rx_json(method, url, **kwargs):
    return rx_request(method, url, **kwargs).map(lambda r: r.json())
