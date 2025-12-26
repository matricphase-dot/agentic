import requests

class PyPITool:
    def get_version(self, package):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json")
            data = response.json()
            return {
                "package": package,
                "version": data['info']['version'],
                "status": "success"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}