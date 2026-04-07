interface MaterialListProps {
  files: File[];
  onRemove: (index: number) => void;
}

export function MaterialList({ files, onRemove }: MaterialListProps) {
  if (!files.length) {
    return <p className="muted">未添加辅助素材</p>;
  }

  return (
    <ul className="material-list">
      {files.map((file, index) => (
        <li key={`${file.name}-${index}`}>
          <span>{file.name}</span>
          <button type="button" className="ghost-button" onClick={() => onRemove(index)}>
            移除
          </button>
        </li>
      ))}
    </ul>
  );
}
