from click.testing import CliRunner
from cli import healthcheck, handle_response

runner = CliRunner()
result = runner.invoke(healthcheck())
#assert result.exit_code == 0 
print(result)
print("done") 