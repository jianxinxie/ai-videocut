interface VideoPlayerProps {
  videoUrl: string | null;
  metadataUrl: string | null;
}

export function VideoPlayer({ videoUrl, metadataUrl }: VideoPlayerProps) {
  return (
    <section className="panel result-panel">
      <div className="section-kicker">结果</div>
      {videoUrl ? (
        <>
          <video controls src={videoUrl} />
          <div className="result-actions">
            <a className="submit-button link-button" href={videoUrl} download>
              下载视频
            </a>
            {metadataUrl && (
              <a className="ghost-button link-button" href={metadataUrl} target="_blank" rel="noreferrer">
                metadata.json
              </a>
            )}
          </div>
        </>
      ) : (
        <p className="muted">成片完成后可播放和下载</p>
      )}
    </section>
  );
}
