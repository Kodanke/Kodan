import pandas as pd
import streamlit as st
import plotly.express as px

# 데이터 읽기
df = pd.read_csv("analysis_result.csv")
df["측정시각"] = pd.to_datetime(df["측정시각"])

# 제목과 설명
st.title("철도 데이터 분석 대시보드")
st.write("교육용 가상 자료입니다. AI 확인후보는 고장 확정이 아닙니다.")

# ★ 설비 선택
equipment = st.selectbox("설비 선택", df["설비ID"].unique())
view = df[df["설비ID"] == equipment]

# ★ 기간 선택 (처음 값: 자료의 첫날 ~ 마지막 날)
start = st.date_input("시작일", view["측정시각"].min().date())
end = st.date_input("종료일", view["측정시각"].max().date())

# ★ 시작일과 종료일을 모두 포함해 조회
view = view[(view["측정시각"].dt.date >= start) & (view["측정시각"].dt.date <= end)]

# ★ 조회 결과
st.write("조회 행 수:", len(view))
if len(view) == 0:
    st.warning("조회 결과가 없습니다. 날짜를 다시 선택하세요.")
st.dataframe(view)

# ★ AI 점검 후보
st.subheader("AI 점검 후보")
candidates = view[view["AI결과"] == "확인후보"]
st.metric("AI 확인후보 건수", len(candidates))
st.dataframe(view["AI결과"].value_counts())

fig = px.line(view, x="측정시각", y="온도_C", title="온도 추이와 AI 확인후보")
fig.add_scatter(x=candidates["측정시각"], y=candidates["온도_C"],
                mode="markers", name="확인후보", marker=dict(color="red", size=10))
st.plotly_chart(fig)
st.dataframe(candidates)

# ★ 다음 1시간 온도 예측
st.subheader("다음 1시간 온도 예측")
pred = view.dropna(subset=["다음온도_C", "AI예측온도_C"])   # 실제·예측이 모두 있는 행
mae = (pred["다음온도_C"] - pred["AI예측온도_C"]).abs().mean()
st.metric("평균 절대 오차(MAE)", f"{mae:.2f} ℃")
st.write("비교한 자료:", len(pred), "건")

fig2 = px.line(pred, x="목표시각", y=["다음온도_C", "AI예측온도_C"], title="실제 온도와 AI 예측 온도")
st.plotly_chart(fig2)

# ★ 업무 메모와 보고서
st.subheader("업무 검토 및 저장")
note = st.text_area("확인할 사항 및 조치 제안", "센서 상태와 운전 조건을 확인한 후 담당자 검토가 필요합니다.")

report = f"""설비: {equipment}
조회 기간: {start} ~ {end}
조회 건수: {len(view)}건
AI 확인후보: {len(candidates)}건
온도 예측 MAE: {mae:.2f} ℃ ({len(pred)}건 비교)
업무 메모: {note}
교육용 가상 자료이며, 확인후보는 고장 확정이 아닙니다."""
st.text(report)

# ★ 파일 내려받기 (현재 조회 결과만)
st.download_button("조회 결과 CSV", view.to_csv(index=False).encode("utf-8-sig"), "dashboard_result.csv")
st.download_button("점검 후보 CSV", candidates.to_csv(index=False).encode("utf-8-sig"), "inspection_candidates.csv")
st.download_button("보고서 TXT", report.encode("utf-8-sig"), "dashboard_report.txt")
