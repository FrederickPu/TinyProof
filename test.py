from lean_dojo import LeanGitRepo, trace

if __name__ == "__main__":
    repo = LeanGitRepo("https://github.com/yangky11/lean4-example", "7b6ecb9ad4829e4e73600a3329baeb3b5df8d23f")
    trace(repo, dst_dir="traced_lean4-example")