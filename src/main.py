import argparse

def video_rank():
    print("执行视频排行榜相关操作...")

def main():
    parser = argparse.ArgumentParser(description="Bilibili Crawler")
    parser.add_argument('--mode', type=str, required=True, help='运行模式: video_rank等')
    args = parser.parse_args()

    if args.mode == 'video_rank':
        video_rank()
    else:
        print(f"未知的mode: {args.mode}")

if __name__ == "__main__":
    main()