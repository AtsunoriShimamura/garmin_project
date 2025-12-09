# fetch_garmin_activities.py
from datetime import date, timedelta
from pathlib import Path
import os
import json
import shutil  # 追加

import pandas as pd
from dotenv import load_dotenv
from garminconnect import Garmin

from .mailer import send_weekly_csv


# ========= パス周りの共通設定 =========

# このファイル(src配下)から見て1つ上 = プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# data 配下
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = DATA_DIR / "exports"

# 必要ならフォルダを自動作成
for d in [RAW_DIR, PROCESSED_DIR, EXPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def _create_client() -> Garmin:
    """Garmin Connect にログイン済みクライアントを返す内部関数"""

    # src 配下の .env を読む
    load_dotenv(PROJECT_ROOT / "src" / ".env")

    username = os.environ["GARMIN_USERNAME"]
    password = os.environ["GARMIN_PASSWORD"]

    client = Garmin(username, password)
    client.login()
    return client


def fetch_activity_list(days: int = 7) -> pd.DataFrame:
    """
    直近 days 日分のアクティビティ一覧を DataFrame で返す（1行=1アクティビティ）
    """
    client = _create_client()

    end = date.today()
    start = end - timedelta(days=days)

    activities = client.get_activities_by_date(start.isoformat(), end.isoformat())
    df = pd.DataFrame(activities)
    return df


def _details_to_timeseries(details: dict) -> pd.DataFrame:
    """
    get_activity_details() の戻り値 details から
    センサー時系列の DataFrame を作る。
    1行=サンプル（だいたい1秒ごと）、列=各種メトリクス。
    """
    descs = details["metricDescriptors"]
    metrics = details["activityDetailMetrics"]

    # metricsIndex -> key の対応表
    index_to_key: dict[int, str] = {
        d["metricsIndex"]: d["key"] for d in descs
    }

    rows: list[dict] = []
    for m in metrics:
        arr = m["metrics"]  # 長さ23前後の配列
        row: dict[str, float] = {}
        for idx, value in enumerate(arr):
            if value is None:
                continue
            key = index_to_key.get(idx)
            if key is None:
                continue
            row[key] = value
        rows.append(row)

    df = pd.DataFrame(rows)

    # directTimestamp があれば datetime に変換
    if "directTimestamp" in df.columns:
        df["time"] = pd.to_datetime(df["directTimestamp"], unit="ms")

    return df


def fetch_activity_timeseries(activity_id: int) -> pd.DataFrame:
    """
    指定した activity_id の「時系列データ」を DataFrame で返す。
    列の例: time, sumDistance, directSpeed, directHeartRate, directRunCadence, ...
    """
    client = _create_client()
    details = client.get_activity_details(activity_id)
    df_ts = _details_to_timeseries(details)
    return df_ts


def build_weekly_summary(days: int = 7) -> dict:
    client = _create_client()

    end = date.today()
    start = end - timedelta(days=days)

    acts = client.get_activities_by_date(start.isoformat(), end.isoformat())

    runs = []
    total_dist = 0
    total_time_min = 0

    for a in acts:
        t = a.get("activityType", {}).get("typeKey")
        if t != "running":
            continue

        dist_km = (a.get("distance") or 0) / 1000
        dur_min = (a.get("duration") or 0) / 60
        avg_speed = a.get("averageSpeed") or 0
        avg_pace = 1000 / avg_speed / 60 if avg_speed > 0 else None

        run = {
            "activity_id": a["activityId"],
            "name": a.get("activityName"),
            "start_time_local": a.get("startTimeLocal"),
            "distance_km": round(dist_km, 2),
            "duration_min": round(dur_min, 1),
            "avg_pace_min_per_km": round(avg_pace, 2) if avg_pace else None,
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "avg_power": a.get("avgPower"),
            "training_effect_aerobic": a.get("aerobicTrainingEffect"),
            "training_effect_anaerobic": a.get("anaerobicTrainingEffect"),
        }

        runs.append(run)
        total_dist += dist_km
        total_time_min += dur_min

    return {
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "activity_count": len(runs),
        "total_distance_km": round(total_dist, 1),
        "total_duration_min": round(total_time_min, 1),
        "activities": runs,
    }


def export_weekly_summary_csv(
    days: int = 7,
    out_path: Path | str = PROCESSED_DIR / "weekly_summary.csv",
) -> None:
    """
    直近 days 日分のランニングサマリを CSV として出力する。

    含める列:
      - date: 実施日 (start_time_local の日付部分)
      - name: アクティビティ名
      - distance_km: 距離 [km]
      - duration_min: 時間 [分]
      - avg_pace_min_per_km: 平均ペース [min/km]
      - avg_hr: 平均心拍数
      - max_hr: 最大心拍数
      - avg_power: 平均パワー
      - training_effect_aerobic: 有酸素TE
      - training_effect_anaerobic: 無酸素TE
    """
    summary = build_weekly_summary(days=days)
    acts = summary.get("activities", [])

    if not acts:
        print("対象期間内のランニングがありません。")
        return

    df = pd.DataFrame(acts)

    # start_time_local から「日付だけ」の列を追加
    if "start_time_local" in df.columns:
        df["date"] = df["start_time_local"].str.slice(0, 10)
        # 見やすいように列順を並べ替え
        cols = [
            "date",
            "name",
            "distance_km",
            "duration_min",
            "avg_pace_min_per_km",
            "avg_hr",
            "max_hr",
            "avg_power",
            "training_effect_aerobic",
            "training_effect_anaerobic",
            "activity_id",
            "start_time_local",
        ]
        cols = [c for c in cols if c in df.columns]
        df = df[cols]

    df.to_csv(out_path, index=False, encoding="cp932")
    print(f"{len(df)}本のランを {out_path} に出力しました。")


if __name__ == "__main__":
    # 週間サマリCSVを作成して、そのCSVをメールで送信する簡易フロー

    # 分析用は processed に保存
    processed_csv = PROCESSED_DIR / "weekly_summary.csv"
    export_weekly_summary_csv(days=7, out_path=processed_csv)

    # メール送信用に exports にコピー
    export_csv = EXPORT_DIR / "weekly_summary.csv"
    shutil.copy(processed_csv, export_csv)

    # 宛先は基本 .env の MAIL_TO を使う
    # 別アドレスに送りたい場合は send_weekly_csv(export_csv, "other@example.com")
    send_weekly_csv(export_csv)
