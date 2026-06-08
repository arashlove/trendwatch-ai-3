type BackendStatusProps = {
  connected: boolean;
  message: string;
  checkedAt: string | null;
};

export const BackendStatus = ({
  connected,
  message,
  checkedAt,
}: BackendStatusProps) => (
  <div className="flex items-center justify-between gap-2 text-xs text-gray-600 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700 pb-2 mb-4">
    <div className="flex items-center gap-2">
      <span
        className={`inline-block w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
      />
      <span>{connected ? 'Connected' : 'Offline'} — {message}</span>
    </div>
    {checkedAt ? (
      <span className="text-gray-400">{new Date(checkedAt).toLocaleTimeString()}</span>
    ) : null}
  </div>
);
