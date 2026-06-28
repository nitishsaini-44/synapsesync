/**
 * Opens a pre-filled email compose window.
 * - On mobile: uses mailto: which triggers the native Gmail/mail app.
 * - On desktop: opens the Gmail web compose window.
 */
export const openMail = ({ to, subject, body }) => {
  const encodedSubject = encodeURIComponent(subject);
  const encodedBody = encodeURIComponent(body);

  const isMobile = /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(
    navigator.userAgent
  );

  if (isMobile) {
    // On mobile, mailto: opens the default mail app (Gmail, Apple Mail, etc.)
    window.location.href = `mailto:${to}?subject=${encodedSubject}&body=${encodedBody}`;
  } else {
    // On desktop, open Gmail web compose in a new tab
    window.open(
      `https://mail.google.com/mail/?view=cm&fs=1&to=${to}&su=${encodedSubject}&body=${encodedBody}`,
      '_blank',
      'noopener,noreferrer'
    );
  }
};
