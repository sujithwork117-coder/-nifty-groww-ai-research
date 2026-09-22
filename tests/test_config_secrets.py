from app.config import _secret_file_values


def test_secret_file_supports_env_and_labeled_formats(tmp_path):
    secret_file=tmp_path/"secrets.txt"
    secret_file.write_text("GROWW_API_KEY=key\napi secret - secret\n")

    values=_secret_file_values(secret_file)

    assert values=={"GROWW_API_KEY":"key","GROWW_API_SECRET":"secret"}