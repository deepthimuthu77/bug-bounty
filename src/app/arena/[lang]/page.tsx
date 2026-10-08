import React from 'react';
import ArenaClient from '@/components/ArenaClient';

export const instant = false;

export default async function Page({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  return <ArenaClient lang={lang} />;
}
