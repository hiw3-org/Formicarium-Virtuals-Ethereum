import Main from '@/components/dashboard/main';
import { redirect } from 'next/navigation';
import { getUserDetails, getUser } from '@/utils/supabase/queries';
import { createClient } from '@/utils/supabase/server';
import Home from '@/components/dashboard/home';

export default async function Account() {

    return <Home/>;
}
