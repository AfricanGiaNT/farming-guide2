import React from 'react';
import { ToastNotification } from '../../types';
import Toast from './Toast';

interface ToastContainerProps {
  notifications: ToastNotification[];
  onRemove: (id: string) => void;
}

function ToastContainer({ notifications, onRemove }: ToastContainerProps) {
  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map(notification => (
        <Toast
          key={notification.id}
          notification={notification}
          onClose={() => onRemove(notification.id)}
        />
      ))}
    </div>
  );
}

export default ToastContainer;