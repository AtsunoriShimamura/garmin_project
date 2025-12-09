# analyze_activity.py
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .fetch_garmin_activities import (
    fetch_activity_list,
    fetch_activity_timeseries,
)

# ========= パス周りの共通設定 =========

# このファイル(src配下)から見て1つ上 = プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# data 配下
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FIGURE_DIR = DATA_DIR / "figures"

# 必要ならフォルダを自動作成
for d in [RAW_DIR, FIGURE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def pick_activity() -> int:
    """直近のアクティビティ一覧を表示して、どれを解析するか選ぶ例"""
    df_acts = fetch_activity_list(days=7)

    cols = ["activityId", "activityName", "startTimeLocal", "distance"]
    print(df_acts[cols])

    # 最新のアクティビティを選択
    activity_id = int(df_acts.iloc[0]["activityId"])
    print(f"\n解析対象 activityId: {activity_id}")
    return activity_id


def make_pace_hr_plot(df_ts: pd.DataFrame) -> Path:
    """
    時系列DFから ペース[min/km] & HR[bpm] のグラフを描く。

    - data/figures/pace_hr_plot.png に保存
    - ついでに plt.show() で画面表示もする
    """

    if "directSpeed" not in df_ts.columns or "directHeartRate" not in df_ts.columns:
        raise ValueError("directSpeed または directHeartRate が含まれていません。")

    mask = df_ts["directSpeed"] > 0

    # ペース計算
    df_ts.loc[mask, "pace_sec_per_km"] = 1000.0 / df_ts.loc[mask, "directSpeed"]
    df_ts["pace_min_per_km"] = df_ts["pace_sec_per_km"] / 60.0

    fig, ax1 = plt.subplots()

    ax1.plot(
        df_ts.loc[mask, "time"],
        df_ts.loc[mask, "pace_min_per_km"],
        label="Pace [min/km]",
    )
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Pace [min/km]")
    ax1.invert_yaxis()

    ax2 = ax1.twinx()
    ax2.plot(
        df_ts.loc[mask, "time"],
        df_ts.loc[mask, "directHeartRate"],
        label="Heart Rate [bpm]",
    )
    ax2.set_ylabel("Heart Rate [bpm]")

    plt.title("Pace & Heart Rate vs Time")
    plt.tight_layout()

    # 図の保存先: data/figures/pace_hr_plot.png
    out_path = FIGURE_DIR / "pace_hr_plot.png"
    plt.savefig(out_path)
    print(f"Pace/HR プロットを保存しました: {out_path}")

    plt.show()
    return out_path


if __name__ == "__main__":
    activity_id = pick_activity()
    df_ts = fetch_activity_timeseries(activity_id)
    make_pace_hr_plot(df_ts)
